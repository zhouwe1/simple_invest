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
    """用户持仓趋势-页面"""
    uas = UserAsset.query.filter_by(user_id=current_user.id, is_delete=False).order_by(UserAsset.update_time.desc()).all()
    return render_template(
        'analyse/trend_ua.html',
        uas=uas,
    )


@analyse_blueprint.route('/trend/ua/<string:ua_id>')
@login_required
def trend_ua_detail(ua_id):
    """用户持仓趋势-数据"""
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
    """用户总额趋势-页面"""
    return render_template('analyse/trend_amount.html')


@analyse_blueprint.route('/trend/amount/data')
@login_required
def trend_amount_data():
    """用户总额趋势-数据"""
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
    differences = []
    compare_target = 0
    for index, date_uaa in enumerate(uaa_list):
        amount = round(date_uaa.get('amount'), 2)
        labels.append('{}({})'.format(date_uaa.get('date'), date_uaa.get('count')))
        datas.append(amount)
        if index:
            differences.append(round((amount - compare_target), 2))
        else:
            differences.append(0)
        compare_target = amount
    return jsonify({'code': 0, 'labels': labels, 'datas': datas, 'differences': differences})


@analyse_blueprint.route('/scale')
def scale():
    """用户占比-页面"""
    asset_summary = current_user.asset_summary
    family_members = current_user.family_members  # 用户的家庭成员
    agent_list = []
    fptype_list = []
    amount_total = asset_summary.get('total_amount')

    # 渠道占比
    agent_tuples = asset_summary.get('agent_tuples')
    for name, amount, count in agent_tuples:
        agent_list.append({
            'name': name,
            'amount': amount,
            'count': count,
            'rate': round(amount / amount_total * 100, 2)
        })

    # 类型占比
    family_members_fptype_list = []
    family_amount = 0
    for member in family_members:
        member_fptype_list = []
        fptype_tuples = member.asset_summary.get('fptype_tuples')
        family_amount += member.asset_summary.get('total_amount')

        for name, amount, count in fptype_tuples:
            member_fptype_list.append({
                'name': name,
                'amount': amount,
                'count': count,
                'rate': round(amount / amount_total * 100, 2),
            })

        family_members_fptype_list.append(member_fptype_list)
        if member.id == current_user.id:
            fptype_list = member_fptype_list

    if len(family_members_fptype_list) > 1:
        family_fptype_dict = dict()
        for member_fptype_list in family_members_fptype_list:
            for fptype in member_fptype_list:
                fptype_name = fptype.get('name')
                if fptype_name in family_fptype_dict:
                    family_fptype_dict[fptype_name]['amount'] += fptype.get('amount')
                    family_fptype_dict[fptype_name]['count'] += fptype.get('count')
                else:
                    family_fptype_dict[fptype_name] = fptype.copy()
                family_fptype_dict[fptype_name]['rate'] = round(family_fptype_dict[fptype_name]['amount'] / family_amount * 100, 2)
        family_fptype_list = list(family_fptype_dict.values())
        family_fptype_list.sort(key=lambda x: x.get('amount'), reverse=True)
    else:
        family_fptype_list = []

    return render_template(
        'analyse/scale.html',
        agent_list=agent_list,
        fptype_list=fptype_list,
        family_fptype_list=family_fptype_list,
    )
