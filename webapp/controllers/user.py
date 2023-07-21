from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.sql import desc
from werkzeug.exceptions import BadRequest
from webapp.models.user_models import Family
from webapp.models.financing_models import Agent, FinancialProduct, UserAsset, UAAmount, UADetail, FPType
from webapp.extentions import db
from webapp.functions.logs import logger
from webapp.functions.public import str2dt
import traceback


user_blueprint = Blueprint(
    'user',
    __name__
)


@user_blueprint.route('/holdings')
@login_required
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


@user_blueprint.route('/holdings/update', methods=['POST'])
@login_required
def holdings_update():
    form = request.form
    user = current_user
    ua_id = form.get('id')
    amount = float(form.get('amount')) * 100

    if ua_id == '0':
        # 走新增接口进来的，添加新的持仓记录，或者恢复已删除的记录
        agent_id = form.get('agent', type=int)
        fp_name = form.get('fp')

        agent_name = Agent.name_cache().get(agent_id)
        if not agent_name:
            return jsonify({'code': 1, 'msg': '购买渠道错误'})
        fp = FinancialProduct.query.filter_by(name=fp_name).first()
        if not fp:
            return jsonify({'code': 1, 'msg': '理财产品错误'})

        ua = UserAsset.query.filter_by(agent_id=agent_id, fp=fp.id, user_id=user.id).first()

        if ua and not ua.is_delete:
            # 存在相同理财产品，相同渠道，未删除的记录
            return jsonify({'code': 1, 'msg': '已在{}购买过{}，不要重复添加'.format(agent_name, fp.name)})
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


@user_blueprint.route('/holdings/details')
@login_required
def holdings_details():
    """用户理财产品明细"""
    form = request.args
    query_dict = {'user_id': current_user.id}

    if form.get('agent'):
        query_dict['agent_id'] = form.get('agent')

    query_options = [
        UserAsset.user_id == current_user.id,
        UserAsset.id == UADetail.userasset_id
    ]
    if form.get('agent'):
        query_options.append(UserAsset.agent_id == form.get('agent'))
    details = UADetail.query.join(UserAsset).filter(*query_options).order_by(UADetail.expiration.asc(), UADetail.id.desc()).all()
    return render_template(
        'user/holdings_details.html',
        details=details,
        uas=UserAsset.query.filter_by(user_id=current_user.id, is_delete=False).all(),
        user_agents=Agent.user_agent(current_user.id),
        fp_types=FPType.dict(),
    )


@user_blueprint.route('/holdings/details', methods=['DELETE'])
@login_required
def holdings_details_delete():
    form = request.form
    user = current_user
    detail_id = form.get('id')
    detail = UADetail.get(detail_id, user.id)
    db.session.delete(detail)
    db.session.commit()
    return jsonify({'code': 0})


@user_blueprint.route('/holdings/details/update', methods=['POST'])
@login_required
def holdings_details_update():
    form = request.form
    user = current_user
    detail_id = form.get('id')
    name = form.get('name', '')
    amount = float(form.get('amount')) * 100
    expiration = form.get('expiration')
    expiration = str2dt(expiration)
    whatever = form.get('whatever')  # 预留

    if detail_id == '0':
        ua_name = form.get('ua')
        agent, ua_name = ua_name.split(':')
        ua = UserAsset.query.join(FinancialProduct).filter(FinancialProduct.name==ua_name, FinancialProduct.id==UserAsset.fp, UserAsset.user_id==user.id).first()
        if not ua:
            raise BadRequest('理财产品错误')
        detail = UADetail(ua.id, name, expiration, amount)
        fp_name = ua.fp_name
        agent_name = ua.agent_name
    else:
        detail = UADetail.get(detail_id, user.id)
        detail.name = name
        detail.amount = amount
        detail.expiration = expiration
        if whatever:
            meta = detail.meta.copy()
            meta.update({'whatever': whatever})
            detail.meta = meta
        db.session.commit()
        fp_name = ''
        agent_name = ''

    return jsonify({
        'code': 0,
        'id': detail.id,
        'agent_name': agent_name,
        'fp_name': fp_name,
        'name': detail.name,
        'amount': str(detail.amount_yuan),
        'expiration': detail.expiration.strftime('%Y-%m-%d'),
    })


@user_blueprint.route('/family', methods=['POST', 'GET'])
@login_required
def family_index():
    family = current_user.family
    if request.method == 'GET':
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
            family_summary['goal_rate'] = round(family_summary['goal_rate'], 2)
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
    elif request.method == 'POST':
        form = request.form
        if family:
            key = form.get('key')
            value = form.get('value')
            if key == 'goal':
                value = int(value) * 100
            setattr(family, key, value)
            db.session.commit()
        return jsonify({'code': 0, 'msg': '修改成功'})


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
