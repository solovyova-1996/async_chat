import os
import sys
from logging import getLogger, Formatter, INFO, DEBUG, StreamHandler
from pathlib import Path
from logging import handlers

from general.variables import ENCODING

sys.path.append('../')
path = Path(__file__).parents[1]
path = os.path.join(path, 'log', 'server.log')

# создаем logger с именем server
log = getLogger('server')
# устанавливаем уровень для регистратора
log.setLevel(DEBUG)
# создаем экземпляр класса Formatter для создания нужного формата
formatter = Formatter(
    "%(asctime)-8s %(levelname)s(%(levelno)s) %(module)-12s %(message)s")
# создаем обработчик для ротации лог-файлов один раз в день
handler_server_log = handlers.TimedRotatingFileHandler(filename=path, when='D',
                                                       interval=1,
                                                       backupCount=100,encoding=ENCODING)
handler_server_log_stdout = StreamHandler(sys.stdout)
handler_server_log_stdout.setFormatter(formatter)
handler_server_log_stdout.setLevel(DEBUG)
# добавляем формат обработчику
handler_server_log.setFormatter(formatter)
# добавляем уровень обработчику
handler_server_log.setLevel(DEBUG)
# добавляем обработчик к регистратору
log.addHandler(handler_server_log)
# log.addHandler(handler_server_log_stdout)

if __name__ == '__main__':
    log.critical('new_messages')
    log.error('error_message')
    log.debug('debug-messages')
