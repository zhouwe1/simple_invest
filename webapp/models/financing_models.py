from sqlalchemy import UniqueConstraint, desc
from webapp.extentions import db


class UserAsset(db.Model):
    """
    用户投资项目
    """
    id = db.Column(db.Integer(), primary_key=True)
    agent_id = db.Column(db.Integer(), db.ForeignKey('agent.id', ondelete='RESTRICT'), nullable=False)
    fp = db.Column(db.Integer(), db.ForeignKey('financial_product.id', ondelete='RESTRICT'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True))  # 第一次买入时间
    update_time = db.Column(db.DateTime(timezone=True), index=True)  # 最后更新时间
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=False)
    amounts = db.relationship(
        'UAAmount',
        backref='user_asset',
        lazy='dynamic'
    )

    __table_args__ = (
        UniqueConstraint('fp', 'user_id', name='uix_fp_user'),  # 联合唯一索引
    )


    @property
    def last_amount(self):
        return self.amounts.order_by(desc('id')).first()


class UAAmount(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date())
    userasset_id = db.Column(db.Integer(), db.ForeignKey('user_asset.id', ondelete='RESTRICT'), nullable=False)
    amount = db.Column(db.Integer(), default=0)
    update_time = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint('userasset_id', 'date', name='uix_uaid_date'),  # 联合唯一索引
    )


class Agent(db.Model):
    """购买处(银行/基金公司/支付宝/微信)"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), unique=True)
    assets = db.relationship(
        'UserAsset',
        backref='agent',
        lazy='dynamic'
    )

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()


fp_assets = db.Table(
    'fp_assets',
    db.Column('fp_id', db.Integer(), db.ForeignKey('financial_product.id'), nullable=False),
    db.Column('fpa_id', db.Integer(), db.ForeignKey('fp_asset.id'), nullable=False),
    UniqueConstraint('fp_id', 'fpa_id', name='fp_fpa_unique')  # 联合唯一索引,name索引的名字
)


class FinancialProduct(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32), unique=True)
    code = db.Column(db.Integer(), unique=True)  # 基金/股票 代码
    type_id = db.Column(db.Integer(), db.ForeignKey('fp_type.id', ondelete='RESTRICT'), nullable=False)
    url = db.Column(db.Text(), default='{}')
    meta = db.Column(db.Text(), default='{}')
    update_time = db.Column(db.DateTime(timezone=True))  # 更新时间
    assets = db.relationship(
        'FPAsset',
        secondary=fp_assets,
        backref=db.backref('fps', lazy='dynamic')
    )
    us_assets = db.relationship(
        'UserAsset',
        backref='financial_product',
        lazy='dynamic'
    )

    def __init__(self, name, type_id, code=None):
        self.name = name
        self.type_id = type_id
        self.code = code
        db.session.add(self)
        db.session.commit()


class FPAsset(db.Model):
    """
    金融产品的资产分布枚举： 股票、债券、现金、其他
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), unique=True)


class FPType(db.Model):
    """
    理财产品类型
    0其他/ 1基金/ 2股票/ 3银行理财/ 4保险理财
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(8), unique=True)
    fps = db.relationship(
        'FinancialProduct',
        backref='type',
        lazy='dynamic'
    )
