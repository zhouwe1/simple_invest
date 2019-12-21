from flask import Blueprint, render_template, request, redirect, url_for, session, abort, flash
from flask_login import login_user, logout_user, current_user, login_required
from webapp.models import User


home_blueprint = Blueprint(
    'home',
    __name__
)


@home_blueprint.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            if user.totp_key:
                # 进行二次验证
                session['login_user_2step'] = user.id
                return redirect(url_for('user.two_step', next=request.args.get('next')))

            login_user(user)
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('pic.home'))
        else:
            pass

    return render_template('login.html')


@home_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.login'))
