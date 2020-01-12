from libgravatar import Gravatar
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone('Asia/Shanghai')


def get_avatar(email):
    """获取用户头像"""
    g = Gravatar(email)
    return g.get_image(size=84, default='mm')


def now():
    return datetime.now(tz=TIMEZONE)
