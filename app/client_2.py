import json
import sys
from argparse import ArgumentParser
from json import JSONDecodeError
from logging import getLogger
import socket
from time import time, sleep
import threading

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from client.database import ClientDatabase
from client.general_window import ClientGeneralWindow
from client.start_dialog import UserNameDialog
from client.transport import ClientTransport
from descriptors import Port
from errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError
from general.utils import send_mesages, get_messages
from decorators_log import log_func
from general.variables import ACTION, GREETINGS, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE_TEXT, MESSAGE, \
    SENDER, EXIT, DESTINATION

from config import client_log_config
from metaclasses import ClientVerifier

log = getLogger('client')


@log_func
def argv_parser():
    # создаем парсер командной строки
    argv_pars = ArgumentParser()
    # создаем аргументы парсера - порт
    argv_pars.add_argument('port', default=DEFAULT_PORT,
                           help='port on which to run', type=int, nargs='?')
    # создаем аргумент парсера ip адресс
    argv_pars.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    # создаем аргумент парсера mode (listen or send)
    argv_pars.add_argument('-n', '--name', nargs='?')
    # передаем парсеру параметры командной строки
    ip_and_port_and_mode = argv_pars.parse_args(sys.argv[1:])
    server_port = ip_and_port_and_mode.port
    server_ip_addr = ip_and_port_and_mode.addr
    client_name = ip_and_port_and_mode.name
    return server_ip_addr, server_port, client_name


if __name__ == '__main__':
    # загружаем параметры переданные в командной строке
    ip, port, client_name = argv_parser()
    # создание приложения
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.png'))

    # если не указано имя пользователя, то запрашиваем его
    if not client_name:
        start_dialog = UserNameDialog()
        app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)
    log.info(f'Запущен клиент с парамертами: адрес сервера: {ip} , порт: {port}, имя пользователя: {client_name}')
    # создаем базу данных
    database = ClientDatabase(client_name)
    try:
        transport = ClientTransport(port,ip,database,client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    general_window = ClientGeneralWindow(database,transport)
    general_window.make_connection(transport)
    general_window.setWindowTitle(f'Чат программа - {client_name}')
    app.exec_()

    transport.transport_shutdown()
    transport.join()
