from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from flask_login import current_user, login_required
from webapp.models.financing_models import UserAsset


analyse_blueprint = Blueprint(
    'analyse',
    __name__
)


@analyse_blueprint.route('/trend')
@login_required
def trend():
    uas = UserAsset.query.filter_by(user_id=current_user.id, is_delete=False).order_by(UserAsset.update_time.desc()).all()
    return render_template(
        'analyse/trend.html',
        uas=uas,
    )


@analyse_blueprint.route('/trend/<string:ua_id>')
@login_required
def trend_ua(ua_id):
    ua = UserAsset.query.filter_by(user_id=current_user.id, id=ua_id).first()

    labels = []
    datas = []
    for uaa in ua.amounts.all():
        labels.append(uaa.date.strftime('%Y-%m-%d'))
        datas.append(uaa.amount_yuan)
    return jsonify({'code': 0, 'labels': labels, 'datas': datas})

