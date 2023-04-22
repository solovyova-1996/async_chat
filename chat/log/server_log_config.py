import inspect
import logging
from logging.handlers import TimedRotatingFileHandler

log_server = logging.getLogger('server')
log_server.setLevel(logging.DEBUG)
rotate_handler = TimedRotatingFileHandler("log\logs\server.log", when='m', interval=1, backupCount=5)
rotate_handler.suffix = '%Y%m%d'
formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s %(message)s")
rotate_handler.setFormatter(formatter)

log_server.addHandler(rotate_handler)


def log_server_deco(func):
    def wrapper(*args, **kwargs):
        log_server.info(f"Функция {func.__name__} вызвана из функции {inspect.currentframe().f_back.f_code.co_name}")
        return func(*args, **kwargs)

    return wrapper
