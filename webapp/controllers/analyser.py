from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from flask_login import current_user, login_required
from webapp.models.financing_models import UserAsset, Agent, FPType, UAAmount


analyse_blueprint = Blueprint(
    'analyse',
    __name__
)


@analyse_blueprint.route('/trend/ua')
@login_required
def trend_ua_index():
    uas = UserAsset.query.filter_by(user_id=current_user.id, is_delete=False).order_by(UserAsset.update_time.desc()).all()
    return render_template(
        'analyse/trend_ua.html',
        uas=uas,
    )


@analyse_blueprint.route('/trend/ua/<string:ua_id>')
@login_required
def trend_ua_detail(ua_id):
    ua = UserAsset.query.filter_by(user_id=current_user.id, id=ua_id).first()

    labels = []
    datas = []
    for uaa in ua.amounts.all():
        labels.append(uaa.date.strftime('%Y-%m-%d'))
        datas.append(uaa.amount_yuan)
    return jsonify({'code': 0, 'labels': labels, 'datas': datas})


@analyse_blueprint.route('/trend/amount')
@login_required
def trend_amount_index():
    return render_template('analyse/trend_amount.html')


@analyse_blueprint.route('/trend/amount/data')
@login_required
def trend_amount_data():
    uaas = UAAmount.query.join(UserAsset).filter(
        UserAsset.user_id == current_user.id, UserAsset.id == UAAmount.userasset_id).all()
    date_dict = dict()
    for uaa in uaas:
        date = uaa.date.strftime('%Y-%m-%d')
        if date in date_dict:
            date_dict[date]['count'] += 1
            date_dict[date]['amount'] += uaa.amount_yuan
        else:
            date_dict[date] = {
                'count': 1,
                'amount': uaa.amount_yuan,
                'date': date,
            }

    uaa_list = list(date_dict.values())
    uaa_list.sort(key=lambda x: x.get('date'))

    labels = []
    datas = []
    for date_uaa in uaa_list:
        labels.append('{}({})'.format(date_uaa.get('date'), date_uaa.get('count')))
        datas.append(round(date_uaa.get('amount'), 2))
    return jsonify({'code': 0, 'labels': labels, 'datas': datas})


@analyse_blueprint.route('/scale')
def scale():
    agent_dict = {}
    fptype_dict = {}
    amount_total = 0
    for ua in UserAsset.query.filter_by(user_id=current_user.id, is_delete=0).all():
        amount = ua.last_amount.amount_yuan
        agent_id = ua.agent_id
        fpt_id = ua.financial_product.type_id
        amount_total += amount
        if agent_id in agent_dict:
            agent_dict[agent_id]['amount'] += amount
            agent_dict[agent_id]['count'] += 1
        else:
            agent_dict[agent_id] = {
                'id': agent_id,
                'amount': amount,
                'count': 1,
            }

        if fpt_id in fptype_dict:
            fptype_dict[fpt_id]['amount'] += amount
            fptype_dict[fpt_id]['count'] += 1
        else:
            fptype_dict[fpt_id] = {
                'id': fpt_id,
                'amount': amount,
                'count': 1,
            }

    for _, agent in agent_dict.items():
        agent['rate'] = round(agent['amount'] / amount_total * 100, 2)
        agent['name'] = Agent.name_cache().get(agent['id'])

    for _, fptype in fptype_dict.items():
        fptype['rate'] = round(fptype['amount'] / amount_total * 100, 2)
        fptype['name'] = FPType.dict().get(fptype['id'])
    agent_list = list(agent_dict.values())
    fptype_list = list(fptype_dict.values())
    agent_list.sort(key=lambda x: x.get('amount'), reverse=True)
    fptype_list.sort(key=lambda x: x.get('amount'), reverse=True)
    return render_template(
        'analyse/scale.html',
        agent_list=agent_list,
        fptype_list=fptype_list,
    )
