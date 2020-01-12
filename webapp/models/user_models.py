from webapp.extentions import db, cache
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from webapp.functions import public
from .financing_models import UserAsset, FPType, Agent


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
        return public.get_avatar(self.email)

    def refresh_last_login(self):
        self.last_login = public.now()
        db.session.commit()

    @property
    def goal_yuan(self):
        if self.goal:
            return int(self.goal / 100)
        else:
            return 0

    @property
    def asset_summary(self):
        cache_key = 'user_asset_summary_{}'.format(self.id)
        if cache.get(cache_key):
            return cache.get(cache_key)

        asset_dict = {'goal': self.goal_yuan,
                      'fp_count': 0,
                      'total_amount': 0,
                      'last_update': '',
                      'agent_tuples': list(),
                      'fptype_tuples': list(),
                      }
        agent_dict = dict()
        fptype_dict = dict()
        last_update = None
        for ua in UserAsset.query.filter_by(user_id=self.id, is_delete=False).all():
            # 获取最后更新时间
            if not last_update:
                asset_dict['last_update'] = ua.update_time_str
            elif ua.update_time > last_update:
                asset_dict['last_update'] = ua.update_time_str

            amount = ua.last_amount.amount_yuan
            asset_dict['total_amount'] += amount
            asset_dict['fp_count'] += 1

            # 汇总每个渠道的总金额
            agent_id = ua.agent_id
            if agent_id in agent_dict:
                agent_dict[agent_id]['amount'] += amount
                agent_dict[agent_id]['count'] += 1
            else:
                agent_dict[agent_id] = {'amount': amount, 'count': 1}

            # 汇总每个理财类型的总金额
            fp_type_id = ua.financial_product.type_id
            if fp_type_id in fptype_dict:
                fptype_dict[fp_type_id]['amount'] += amount
                fptype_dict[fp_type_id]['count'] += 1
            else:
                fptype_dict[fp_type_id] = {'amount': amount, 'count': 1}

        agent_tuples = []
        for k, v in agent_dict.items():
            agent_tuples.append((Agent.name_cache().get(k), v.get('amount'), v.get('count')))
        agent_tuples.sort(key=lambda x: x[1], reverse=True)
        asset_dict['agent_tuples'] = agent_tuples

        fptype_tuples = []
        for k, v in fptype_dict.items():
            fptype_tuples.append((FPType.dict().get(k), v.get('amount'), v.get('count')))
        fptype_tuples.sort(key=lambda x: x[1], reverse=True)
        asset_dict['fptype_tuples'] = fptype_tuples

        if self.goal:
            goal_rate = round(asset_dict['total_amount'] / self.goal_yuan * 100, 1)
        else:
            goal_rate = 0
        asset_dict['goal_rate'] = goal_rate
        asset_dict['total_amount'] = round(asset_dict.get('total_amount'), 2)
        cache.set(cache_key, asset_dict)
        return asset_dict


class Family(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))
    goal = db.Column(db.Integer(), default=0)
    create_time = db.Column(db.DateTime(timezone=True), default=public.now)
    update_time = db.Column(db.DateTime(timezone=True), default=public.now)
    parent_id = db.Column(db.Integer())
    users = db.relationship(
        'User',
        backref='family',
        lazy='dynamic'
    )

    def __init__(self, parent_id, name, goal):
        """
        创建家庭
        :param name:
        :param goal: 单位:分
        """
        self.parent_id = parent_id,
        self.name = name
        self.goal = goal
        self.create_time = public.now()
        self.update_time = public.now()
        db.session.add(self)
        db.session.flush()

    @property
    def goal_yuan(self):
        return int(self.goal / 100)

    @property
    def parent(self):
        user = User.query.filter_by(id=self.parent_id).first()
        if user:
            return user.username
        else:
            return ''
