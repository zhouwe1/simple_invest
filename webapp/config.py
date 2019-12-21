import configparser
import os.path


BASE_DIR = os.path.abspath('.')

config = configparser.ConfigParser()
config.read(os.path.join('', 'config.ini'))


def try_get(section, option, default=None):
    try:
        return config.get(section, option)
    except (configparser.NoOptionError, configparser.NoSectionError):
        return default


class Config:
    DEBUG = True
    SECRET_KEY = 'S02sS*SJ:#BSH@5sb2#=_23 ^s5<$.>2(#@'

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{pw}@{host}:{port}/{db}?charset=utf8mb4".format(
        user=try_get('database', 'user'),
        pw=try_get('database', 'pass'),
        host=try_get('database', 'host'),
        port=try_get('database', 'port'),
        db=try_get('database', 'db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
