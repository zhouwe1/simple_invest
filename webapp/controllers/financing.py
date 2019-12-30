from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, abort, flash
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import desc
from webapp.models.financing_models import Agent, FinancialProduct, UserAsset, UAAmount, FPType
from webapp.extentions import db
from webapp.functions.logs import logger
import traceback


financing_blueprint = Blueprint(
    'financing',
    __name__
)


@financing_blueprint.route('/')
@login_required
def home():
    return render_template('user.html')


@financing_blueprint.route('/agents')
@login_required
def agent_index():
    agents = Agent.query.order_by(desc('id')).all()
    return render_template(
        'financing/agent_index.html',
        agents=agents,
    )


@financing_blueprint.route('/agent_update', methods=['POST'])
@login_required
def agent_update():
    form = request.form
    agent_id = form.get('id')
    name = form.get('name')

    if Agent.query.filter(Agent.name == name, Agent.id != agent_id).count():
        return jsonify({'code': 1, 'msg': '名称重复'})
    if agent_id == '0':
        agent = Agent(name=name)
    else:
        agent = Agent.query.filter_by(id=agent_id).first()
        agent.name = name
        db.session.commit()
    return jsonify({'code': 0, 'name': agent.name, 'id': agent.id})


@financing_blueprint.route('/agent_delete')
@login_required
def agent_delete():
    agent = Agent.query.filter_by(id=request.args.get('id')).first()
    try:
        db.session.delete(agent)
        db.session.commit()
        return jsonify({'code': 0})
    except IntegrityError:
        return jsonify({'code': 1, 'msg': '持仓中的渠道不允许删除'})


@financing_blueprint.route('/financial_products')
@login_required
def fp_index():
    fps = FinancialProduct.query.order_by(desc('id')).all()
    return render_template(
        'financing/fp_index.html',
        fps=fps,
        fp_types=FPType.query.order_by('id').all(),
    )


@financing_blueprint.route('/fp_update', methods=['POST'])
@login_required
def fp_update():
    form = request.form
    fp_id = form.get('id')
    name = form.get('name')
    fp_type = int(form.get('fp_type'))
    fp_code = form.get('fp_code') or None

    if FinancialProduct.query.filter(FinancialProduct.name == name, FinancialProduct.id != fp_id).count():
        return jsonify({'code': 1, 'msg': '名称重复'})

    if fp_type in (3, 4) and not fp_code:
        return jsonify({'code': 1, 'msg': '股票或基金请填写代码'})

    if fp_code:
        if FinancialProduct.query.filter(FinancialProduct.code == fp_code, FinancialProduct.id != fp_id).count():
            return jsonify({'code': 1, 'msg': '代码重复'})
    if fp_id == '0':
        fp = FinancialProduct(name=name, code=fp_code, type_id=fp_type)
    else:
        fp = FinancialProduct.query.filter_by(id=fp_id).first()
        fp.name = name
        db.session.commit()
    return jsonify({'code': 0, 'name': fp.name, 'id': fp.id, 'fp_type': fp.type.name, 'fp_code': fp.code})


@financing_blueprint.route('/fp_delete')
@login_required
def fp_delete():
    fp = FinancialProduct.query.filter_by(id=request.args.get('id')).first()
    try:
        db.session.delete(fp)
        db.session.commit()
        return jsonify({'code': 0})
    except IntegrityError:
        return jsonify({'code': 1, 'msg': '持仓中的理财产品不允许删除'})


@financing_blueprint.route('/holdings')
def holdings():
    form = request.args
    query_dict = {'user_id': current_user.id, 'is_delete': False}
    # if form.get('fp_type'):
    #     query_dict['fp.type_id'] = form.get('fp_type')

    uas = UserAsset.query.filter_by(**query_dict)
    if form.get('fp_type'):
        uas = uas.join(FPType, FPType.id == form.get('fp_type')).join(FinancialProduct, FinancialProduct.type_id == FPType.id)

    uas = uas.order_by(UserAsset.update_time.desc()).all()
    return render_template(
        'financing/holdings.html',
        uas=uas,
        fps=FinancialProduct.query.order_by(desc('id')).all(),
        agents=Agent.query.order_by('id').all(),
        fp_types=FPType.query.order_by('id').all(),
    )


@financing_blueprint.route('/holdings_update', methods=['POST'])
def holdings_update():
    form = request.form
    user = current_user
    ua_id = form.get('id')
    amount = float(form.get('amount')) * 100

    if ua_id == '0':
        agent_id = form.get('agent')
        fp_name = form.get('fp')

        agent = Agent.query.filter_by(id=agent_id).first()
        if not agent:
            return jsonify({'code': 1, 'msg': '购买渠道错误'})
        fp = FinancialProduct.query.filter_by(name=fp_name).first()
        if not fp:
            return jsonify({'code': 1, 'msg': '理财产品错误'})
        if UserAsset.query.filter_by(agent_id=agent_id, fp=fp.id, user_id=user.id).count():
            return jsonify({'code': 1, 'msg': '已在{}购买过{}，不要重复添加'.format(agent.name, fp.name)})
        try:
            ua = UserAsset(agent_id, fp.id, current_user.id)
            uaa = UAAmount.update(ua.id, amount)
            ua.update_time = uaa.update_time
            db.session.commit()
            return jsonify({
                'code': 0,
                'id': ua.id,
                'name': ua.fp_name,
                'amount': str(ua.last_amount.amount_yuan),
                'update_time': ua.update_time_str,
            })
        except:
            logger.error('add user_asset error: {}'.format(traceback.format_exc()))
            db.session.rollback()
            return jsonify({'code': 1, 'msg': '系统错误'})
    else:
        ua = UserAsset.query.filter_by(id=ua_id, user_id=user.id).first()
        if not ua:
            return jsonify({'code': 1, 'msg': '持仓信息错误'})
        try:
            uaa = UAAmount.update(ua.id, amount)
            ua.update_time = uaa.update_time
            db.session.commit()
            return jsonify({'code': 0, 'amount': str(ua.last_amount.amount_yuan), 'update_time': ua.update_time_str})
        except:
            logger.error('update user_asset error: {}'.format(traceback.format_exc()))
            db.session.rollback()
            return jsonify({'code': 1, 'msg': '系统错误'})


@financing_blueprint.route('/holdings_delete')
def holdings_delete():
    ua = UserAsset.query.filter_by(id=request.args.get('id')).first()
    uaa = UAAmount.update(ua.id, 0)
    ua.update_time = uaa.update_time
    ua.is_delete = True
    db.session.commit()
    return jsonify({'code': 0})
