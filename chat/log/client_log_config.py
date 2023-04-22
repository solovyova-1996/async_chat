import logging

logging.basicConfig(
    filename="log\logs\client.log",
    format="%(asctime)s %(levelname)-5s %(module)s %(message)s",
    level=logging.INFO
)
log_client = logging.getLogger('client')
