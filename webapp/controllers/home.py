from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from webapp.models.user_models import User
from webapp.models.financing_models import UserAsset, FPType


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
    fp_type_dict = dict()
    total_amount = 0  # 总金额
    last_update = None
    fp_count = 0
    for ua in UserAsset.query.filter_by(user_id=current_user.id, is_delete=False).all():
        if not last_update:
            last_update = ua.update_time
        else:
            if ua.update_time > last_update:
                last_update = ua.update_time
        agent_id = ua.agent_id
        agent_name = ua.agent.name
        amount = ua.last_amount.amount_yuan
        fp_type_id = ua.financial_product.type_id
        total_amount += amount
        fp_count += 1
        if agent_id in agent_dict:
            agent_dict[agent_id]['amount'] += amount
            agent_dict[agent_id]['count'] += 1
        else:
            agent_dict[agent_id] = {
                'name': agent_name,
                'amount': amount,
                'count': 1,
            }
        for _, agent in agent_dict.items():
            agent['amount_rate'] = '{}%'.format(round(agent['amount'] / total_amount * 100, 1))

        if fp_type_id in fp_type_dict:
            fp_type_dict[fp_type_id]['amount'] += amount
            fp_type_dict[fp_type_id]['count'] += 1
        else:
            fp_type_dict[fp_type_id] = {
                'amount': amount,
                'name': FPType.dict().get(fp_type_id),
                'count': 1,
            }
        for _, ft_t in fp_type_dict.items():
            ft_t['amount_rate'] = '{}%'.format(round(ft_t['amount'] / total_amount * 100, 1))

    agent_list = list(agent_dict.values())
    agent_list.sort(key=lambda x: x.get('amount'), reverse=True)
    fpt_list = list(fp_type_dict.values())
    fpt_list.sort(key=lambda x: x.get('amount'), reverse=True)
    return render_template(
        'home/dashboard.html',
        target=400000,
        target_rate=round(total_amount/target * 100, 1),
        fp_count=fp_count,
        total_amount=total_amount,
        last_update=last_update,
        agent_list=agent_list,
        fpt_list=fpt_list,
    )
