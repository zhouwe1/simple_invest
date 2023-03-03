from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_FILE = BASE_DIR / 'webapp/financing.db'


class Config:
    DEBUG = True
    SECRET_KEY = 'S02sS*SJ:#BSH@5sb2#=_23 ^s5<$.>2(#@'

    # 数据库
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_RECYCLE = 60
