import inspect
import logging
import sys
import traceback

logger = logging.getLogger('server') if sys.argv[0].find(
    'client') == -1 else logging.getLogger('client')


def log_func(func):
    def deco(*args, **kwargs):
        logging_function = func(*args, **kwargs)
        logger.debug(
            f'Вызванная функция:  {func.__name__} параметры функции: {args} и {kwargs} '
            f'Модуль, из которого вызвана функция: {traceback.format_stack()[0].strip().split()[1][30:39]} '
            f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return logging_function

    return deco


class LogClass:
    def __call__(self, func):
        def deco_func(*args, **kwargs):
            log_function = func(*args, **kwargs)
            logger.debug(f'LogClass:'
                         f'Вызванная функция:  {func.__name__} параметры функции: {args} и {kwargs} '
                         f'Модуль, из которого вызвана функция: {traceback.format_stack()[0].strip().split()[1][30:39]} '
                         f'Вызов из функции {inspect.stack()[1][3]}',
                         stacklevel=2)
            return log_function

        return deco_func
