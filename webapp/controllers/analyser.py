from flask import Blueprint, render_template, jsonify
from flask_login import current_user, login_required
from webapp.models.financing_models import UserAsset, UAAmount


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
    asset_summary = current_user.asset_summary
    agent_list = []
    fptype_list = []
    amount_total = asset_summary.get('total_amount')

    agent_tuples = asset_summary.get('agent_tuples')
    for name, amount, count in agent_tuples:
        agent_list.append({
            'name': name,
            'amount': amount,
            'count': count,
            'rate': round(amount / amount_total * 100, 2)
        })

    fptype_tuples = asset_summary.get('fptype_tuples')
    for name, amount, count in fptype_tuples:
        fptype_list.append({
            'name': name,
            'amount': amount,
            'count': count,
            'rate': round(amount / amount_total * 100, 2),
        })

    return render_template(
        'analyse/scale.html',
        agent_list=agent_list,
        fptype_list=fptype_list,
    )
