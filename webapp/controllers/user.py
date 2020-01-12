from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from webapp.models.user_models import Family
from webapp.extentions import db

user_blueprint = Blueprint(
    'user',
    __name__
)


@user_blueprint.route('/')
@login_required
def home():
    return render_template('user/user.html')


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
