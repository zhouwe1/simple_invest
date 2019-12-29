import logging.handlers
import os.path
from webapp.config import BASE_DIR
from concurrent_log_handler import ConcurrentRotatingFileHandler
file = os.path.join(BASE_DIR, 'log', 'webapp.log')

logger_handle = ConcurrentRotatingFileHandler(file, maxBytes=1024*1024*10, backupCount=5, encoding='utf-8')

fmt = '%(asctime)s [%(name)s] %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s'

# 实例化formatter
formatter = logging.Formatter(fmt)
logger_handle.setFormatter(formatter)

logger = logging.getLogger()  # 获取logger
logger.addHandler(logger_handle)  # 为logger添加handler
logger.setLevel(logging.WARNING)
