from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic
from flask_login import LoginManager

db = SQLAlchemy()
alembic = Alembic()


login_manager = LoginManager()
login_manager.login_view = 'home.login'
login_manager.session_protection = 'basic'
login_manager.login_message = '请登录'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from webapp.models import User
    return User.query.get(user_id)
