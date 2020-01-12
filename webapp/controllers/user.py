from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.sql import desc
from webapp.models.user_models import Family
from webapp.models.financing_models import Agent, FinancialProduct, UserAsset, UAAmount, FPType
from webapp.extentions import db
from webapp.functions.logs import logger
import traceback


user_blueprint = Blueprint(
    'user',
    __name__
)


@user_blueprint.route('/holdings')
def holdings():
    form = request.args
    query_dict = {'user_id': current_user.id, 'is_delete': False}

    if form.get('agent'):
        query_dict['agent_id'] = form.get('agent')

    uas = UserAsset.query.filter_by(**query_dict)
    if form.get('fp_type'):
        uas = uas.join(FinancialProduct).filter(FinancialProduct.type_id == form.get('fp_type'), FinancialProduct.id == UserAsset.fp)

    uas = uas.order_by(UserAsset.update_time.desc()).all()
    return render_template(
        'user/holdings.html',
        uas=uas,
        fps=FinancialProduct.query.order_by(desc('id')).all(),
        agents=Agent.name_cache(),
        user_agents=Agent.user_agent(current_user.id),
        fp_types=FPType.dict(),
    )


@user_blueprint.route('/holdings_update', methods=['POST'])
def holdings_update():
    form = request.form
    user = current_user
    ua_id = form.get('id')
    amount = float(form.get('amount')) * 100

    if ua_id == '0':
        # 走新增接口进来的，添加新的持仓记录，或者恢复已删除的记录
        agent_id = form.get('agent')
        fp_name = form.get('fp')

        agent = Agent.query.filter_by(id=agent_id).first()
        if not agent:
            return jsonify({'code': 1, 'msg': '购买渠道错误'})
        fp = FinancialProduct.query.filter_by(name=fp_name).first()
        if not fp:
            return jsonify({'code': 1, 'msg': '理财产品错误'})

        ua = UserAsset.query.filter_by(agent_id=agent_id, fp=fp.id, user_id=user.id).first()

        if ua and not ua.is_delete:
            # 存在相同理财产品，相同渠道，未删除的记录
            return jsonify({'code': 1, 'msg': '已在{}购买过{}，不要重复添加'.format(agent.name, fp.name)})
        elif ua:
            # 存在相同理财产品，相同渠道，已删除的记录，恢复这条记录
            uaa = UAAmount.update(ua.id, amount)
            ua.update_time = uaa.update_time
            ua.is_delete = False
            db.session.commit()
            return jsonify({
                'code': 0,
                'id': ua.id,
                'agent': ua.agent_name,
                'name': ua.fp_name,
                'amount': str(ua.last_amount.amount_yuan),
                'update_time': ua.update_time_str,
            })
        else:
            # 添加新纪录
            try:
                ua = UserAsset(agent_id, fp.id, current_user.id)
                uaa = UAAmount.update(ua.id, amount)
                ua.update_time = uaa.update_time
                db.session.commit()
                return jsonify({
                    'code': 0,
                    'id': ua.id,
                    'agent': ua.agent_name,
                    'name': ua.fp_name,
                    'amount': str(ua.last_amount.amount_yuan),
                    'update_time': ua.update_time_str,
                })
            except:
                logger.error('add user_asset error: {}'.format(traceback.format_exc()))
                db.session.rollback()
            return jsonify({'code': 1, 'msg': '系统错误'})
    else:
        # 走更新接口进来
        ua = UserAsset.query.filter_by(id=ua_id, user_id=user.id).first()
        if not ua:
            return jsonify({'code': 1, 'msg': '持仓信息错误'})
        try:
            uaa = UAAmount.update(ua.id, amount)
            ua.update_time = uaa.update_time
            if not amount:
                ua.is_delete = True
            db.session.commit()
            return jsonify({'code': 0, 'amount': str(ua.last_amount.amount_yuan), 'update_time': ua.update_time_str, 'is_delete': ua.is_delete})
        except:
            logger.error('update user_asset error: {}'.format(traceback.format_exc()))
            db.session.rollback()
            return jsonify({'code': 1, 'msg': '系统错误'})


@user_blueprint.route('/family')
@login_required
def family_index():
    family = current_user.family
    if family:
        users = family.users.all()
        family_summary = {'goal_yuan': family.goal_yuan, 'total_amount': 0, 'fp_count': 0, 'goal_rate': 0, 'count': 0}
        members = []
        for user in users:
            user_asset = user.asset_summary
            goal_rate = round(user_asset.get('total_amount') / family_summary['goal_yuan'] * 100, 1)
            members.append({
                'avatar': user.avatar,
                'username': user.username,
                'family_goal_rate': goal_rate,
                **user_asset
            })
            family_summary['total_amount'] += user_asset.get('total_amount')
            family_summary['fp_count'] += user_asset.get('fp_count')
            family_summary['count'] += 1
            family_summary['goal_rate'] += goal_rate
        family_summary['total_amount'] = round(family_summary['total_amount'], 2)
        members.sort(key=lambda x: x.get('total_amount'), reverse=True)
    else:
        family_summary = {}
        members = []
    return render_template(
        'user/family.html',
        family=family,
        family_summary=family_summary,
        members=members,
    )


@user_blueprint.route('/family/create', methods=['POST'])
@login_required
def family_create():
    if current_user.family_id:
        return jsonify({'code': 1, 'msg': '请脱离现有的家庭理财项目才能创建'})
    form = request.form
    name = form.get('name')
    goal = int(form.get('goal')) * 100
    family = Family(current_user.id, name, goal)
    current_user.family_id = family.id
    db.session.commit()
    return jsonify({'code': 0})
