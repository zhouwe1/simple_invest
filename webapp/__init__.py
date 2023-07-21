from flask import Flask, session, jsonify
from flask_login import current_user
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy.track_modifications import models_committed
from .extentions import db, alembic, login_manager
from .config import Config
from .models import *

flask_app = Flask(__name__)
flask_app.config.from_object(Config)

db.init_app(flask_app)
alembic.init_app(flask_app)
login_manager.init_app(flask_app)

from .controllers.home import home_blueprint
from .controllers.user import user_blueprint
from .controllers.setting import setting_blueprint
from .controllers.analyser import analyse_blueprint

flask_app.register_blueprint(home_blueprint, url_prefix='')
flask_app.register_blueprint(setting_blueprint, url_prefix='/setting')
flask_app.register_blueprint(user_blueprint, url_prefix='/user')
flask_app.register_blueprint(analyse_blueprint, url_prefix='/analyse')


@flask_app.before_request
def load_avatar():
    if '_user_id' in session and 'avatar' not in session:
        session['avatar'] = current_user.avatar


@models_committed.connect_via(flask_app)
def update_cache(sender, changes):
    try:
        for model, operation in changes:
            model.clear_cache(model, operation)
    except AttributeError:
        pass


@flask_app.errorhandler(HTTPException)
def handle_exp(error):
    if isinstance(error, BadRequest):
        return jsonify({'code': 1, 'msg': error.description})
