from webapp.extentions import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from webapp.functions import public
from .financing_models import UserAsset


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(32), unique=True)
    last_login = db.Column(db.DateTime(timezone=True))
    join_date = db.Column(db.DateTime(timezone=True), default=public.now)
    goal = db.Column(db.Integer(), default=0)
    family_id = db.Column(db.Integer(), db.ForeignKey('family.id', ondelete='RESTRICT'), default=None)

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

    @property
    def holdings_count(self):
        return UserAsset.query.filter(user_id=self.id, is_delete=False).count()

    @property
    def goal_yuan(self):
        return int(self.goal / 100)


class Family(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))
    goal = db.Column(db.Integer(), default=0)
    create_time = db.Column(db.DateTime(timezone=True))
    update_time = db.Column(db.DateTime(timezone=True))
    users = db.relationship(
        'User',
        backref='family',
        lazy='dynamic'
    )

    def __init__(self, name, goal):
        """
        创建家庭
        :param name:
        :param goal:
        """
        self.name = name
        self.goal = goal
        db.session.add(self)
        db.session.commit()

    @property
    def goal_yuan(self):
        return int(self.goal / 100)
