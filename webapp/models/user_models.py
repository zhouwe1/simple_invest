from webapp.extentions import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from webapp.functions import public


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(32), unique=True)
    last_login = db.Column(db.DateTime(timezone=True))

    def __init__(self, username, password, email):
        """
        创建用户
        :param username:
        :param password:
        """
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        """
        验证密码
        :param password: 密码明文
        :return: True or False
        """
        return check_password_hash(self.password, password)

    @property
    def avatar(self):
        return public.get_avatar()

    def refresh_last_login(self):
        self.last_login = public.now()
        db.session.commit()
