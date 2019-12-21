from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from webapp.models import User


home_blueprint = Blueprint(
    'home',
    __name__
)


@home_blueprint.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            login_user(user)
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('home.dashboard'))
        else:
            pass

    return render_template('home/login.html')


@home_blueprint.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        re_password = request.form.get('re_password')

        if not User.query.filter_by(username=username).count():
            if password == re_password:
                user = User(username, password)
                login_user(user)
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('home.dashboard'))
        else:
            pass

    return render_template('home/register.html')


@home_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.login'))


@home_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('home/dashboard.html')
