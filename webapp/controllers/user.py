from flask import Blueprint, render_template, request, redirect, url_for, send_file, session, abort, flash
from flask_login import current_user, login_required
from webapp.models import User


user_blueprint = Blueprint(
    'user',
    __name__
)


@user_blueprint.route('/')
@login_required
def home():
    return render_template('user.html')


