from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from webapp.models.user_models import User
from webapp.models.financing_models import UserAsset, FPType, Agent


home_blueprint = Blueprint(
    'home',
    __name__
)


@home_blueprint.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_trigger = request.form.get('remember')

        if remember_trigger == 'on':
            remember = True
        else:
            remember = False

        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            login_user(user, remember)
            user.refresh_last_login()
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('home.dashboard'))
        else:
            pass

    return render_template('home/login.html')


@home_blueprint.route('/register', methods=['POST', 'GET'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re_password')

        if not User.query.filter_by(username=username).count():
            if not User.query.filter_by(email=email).count():
                if password == re_password:
                    user = User(username, password, email)
                    login_user(user)
                    user.refresh_last_login()
                    session['avatar'] = user.avatar
                    if request.args.get('next'):
                        return redirect(request.args.get('next'))
                    return redirect(url_for('home.dashboard'))
                else:
                    msg = '两次密码输入不一致'
            else:
                msg = '电子邮箱地址已存在'
        else:
            msg = '用户名已存在'

    return render_template(
        'home/register.html',
        msg=msg
    )


@home_blueprint.route('/logout')
@login_required
def logout():
    session.pop('avatar', '')
    logout_user()
    return redirect(url_for('home.login'))


@home_blueprint.route('/')
@login_required
def dashboard():
    target = 400000
    agent_dict = dict()
    fptype_dict = dict()
    total_amount = 0  # 总金额
    last_update = None
    fp_count = 0
    for ua in UserAsset.query.filter_by(user_id=current_user.id, is_delete=False).all():
        # 获取最后更新时间
        if not last_update:
            last_update = ua.update_time
        elif ua.update_time > last_update:
            last_update = ua.update_time

        amount = ua.last_amount.amount_yuan
        total_amount += amount
        fp_count += 1

        # 汇总每个渠道的总金额
        agent_id = ua.agent_id
        if agent_id in agent_dict:
            agent_dict[agent_id] += amount
        else:
            agent_dict[agent_id] = amount

        # 汇总每个理财类型的总金额
        fp_type_id = ua.financial_product.type_id
        if fp_type_id in fptype_dict:
            fptype_dict[fp_type_id] += amount
        else:
            fptype_dict[fp_type_id] = amount

    agent_tuples = []
    for k, v in agent_dict.items():
        agent_tuples.append((Agent.name_cache().get(k), v))
    agent_tuples.sort(key=lambda x: x[1], reverse=True)
    fptype_tuples = []
    for k, v in fptype_dict.items():
        fptype_tuples.append((FPType.dict().get(k), v))
    fptype_tuples.sort(key=lambda x: x[1], reverse=True)
    return render_template(
        'home/dashboard.html',
        target=400000,
        target_rate=round(total_amount/target * 100, 1),
        fp_count=fp_count,
        total_amount=round(total_amount, 2),
        last_update=last_update,
        agent_tuples=agent_tuples,
        fptype_tuples=fptype_tuples
    )
