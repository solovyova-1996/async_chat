import inspect
import logging

logging.basicConfig(
    filename="log\logs\client.log",
    format="%(asctime)s %(levelname)-5s %(module)s %(message)s",
    level=logging.INFO
)
log_client = logging.getLogger('client')


def log_client_deco(func):
    def wrapper(*args, **kwargs):
        log_client.info(f"Функция {func.__name__} вызвана из функции {inspect.currentframe().f_back.f_code.co_name}")
        return func(*args, **kwargs)

    return wrapper
