from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required
from webapp.models.user_models import User


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
    logout_user()
    return redirect(url_for('home.login'))


@home_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('home/dashboard.html')
