from sqlalchemy import UniqueConstraint
from webapp.extentions import db


class UserAsset(db.Model):
    """
    用户投资项目
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32))
    agent_id = db.Column(db.Integer(), db.ForeignKey('agent.id', ondelete='RESTRICT'))
    fp = db.Column(db.Integer(), db.ForeignKey('financial_product.id', ondelete='RESTRICT'))
    start_time = db.Column(db.DateTime(timezone=True))  # 第一次买入时间
    update_time = db.Column(db.DateTime(timezone=True))  # 最后一次买入时间
    amount = db.Column(db.Integer())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='RESTRICT'))


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
    db.Column('fp_id', db.Integer(), db.ForeignKey('financial_product.id')),
    db.Column('fpa_id', db.Integer(), db.ForeignKey('fp_asset.id')),
    UniqueConstraint('fp_id', 'fpa_id', name='fp_fpa_unique')  # 联合唯一索引,name索引的名字
)


class FinancialProduct(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32), unique=True)
    code = db.Column(db.Integer(), unique=True)  # 基金/股票 代码
    type = db.Column(db.Integer(), db.ForeignKey('fp_type.id', ondelete='RESTRICT'))
    url = db.Column(db.Text(), default='{}')
    meta = db.Column(db.Text(), default='{}')
    update_time = db.Column(db.DateTime(timezone=True))  # 更新时间
    assets = db.relationship(
        'FPAsset',
        secondary=fp_assets,
        backref=db.backref('fps', lazy='dynamic')
    )


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
