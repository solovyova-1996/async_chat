import os
import sys
from logging import getLogger, Formatter, DEBUG, StreamHandler, FileHandler
from pathlib import Path
from logging import handlers

from general.variables import ENCODING

sys.path.append('../')
path = Path(__file__).parents[1]
path = os.path.join(path, 'log', 'client.log')

# создаем logger с именем client
log = getLogger('client')
# устанавливаем уровень для регистратора
log.setLevel(DEBUG)
# создаем экземпляр класса Formatter для создания нужного формата
formatter = Formatter(
    "%(asctime)-30s %(levelname)s-%(levelno)-20s %(module)-28s %(message)s")
# создаем обработчик для ротации лог-файлов один раз в день
handler_server_log = FileHandler(filename=path,encoding=ENCODING)
# создаем обработчик для вывода log-сообщений на стандартный поток вывода
handler_stream_server_log = StreamHandler(sys.stdout)
handler_stream_server_log.setFormatter(formatter)
handler_stream_server_log.setLevel(DEBUG)
# добавляем формат обработчику
handler_server_log.setFormatter(formatter)
# добавляем уровень обработчику
handler_server_log.setLevel(DEBUG)
# добавляем обработчик к регистратору
log.addHandler(handler_server_log)
# log.addHandler(handler_stream_server_log)
if __name__ == '__main__':
    log.critical('new_messages')
    log.error('error_message')
    log.debug('debug-messages')
