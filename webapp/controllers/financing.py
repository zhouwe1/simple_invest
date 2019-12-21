from flask import Blueprint, render_template, request, redirect, url_for, session, abort, flash
from flask_login import current_user, login_required
from webapp.models import User


financing_blueprint = Blueprint(
    'financing',
    __name__
)


@financing_blueprint.route('/')
@login_required
def home():
    return render_template('user.html')


