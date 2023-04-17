import logging
from logging.handlers import TimedRotatingFileHandler

log_server = logging.getLogger('server')
log_server.setLevel(logging.DEBUG)
rotate_handler = TimedRotatingFileHandler("log\logs\server", when='m', interval=1,backupCount=5)
rotate_handler.suffix = '%Y%m%d'
formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s %(message)s")
rotate_handler.setFormatter(formatter)

log_server.addHandler(rotate_handler)
