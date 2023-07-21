from datetime import datetime
import pytz
from hashlib import md5
from datetime import datetime

TIMEZONE = pytz.timezone('Asia/Shanghai')


def get_avatar(email):
    """获取用户头像"""
    url = '//cravatar.cn/avatar/' + cravatar_hash(email)
    return url


def cravatar_hash(email):
    return md5(email.encode()).hexdigest()


def now():
    return datetime.now(tz=TIMEZONE)


def str2dt(dt_str):
    dt_str = dt_str.replace('/', '-')
    if len(dt_str) == 10:
        return datetime.strptime(dt_str, '%Y-%m-%d')
