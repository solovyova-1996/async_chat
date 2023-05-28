import os
import sys
import threading
from logging import getLogger
from argparse import ArgumentParser
import socket

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from select import select
from configparser import ConfigParser
from general.utils import get_messages, send_mesages
from general.variables import ACTION, GREETINGS, TIME, USER, ACCOUNT_NAME, \
    ERROR, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, \
    DESTINATION, EXIT, GET_CONTACTS, LIST_INFO, ADD_CONTACT, REMOVE_CONTACT, \
    USERS_REQUEST, RESPONSE_202

from config import server_log_config
from decorators_log import log_func
from gui_server import GeneralWindow, HistoryWindow, ConfigWindow
from metaclasses import ServerVerifier
from server_database import ServerDatabase
from gui_server import gui_create_model_tabel, gui_create_stat_model

log = getLogger('server')
from descriptors import Port, Host

new_connect = False
conflag_lock = threading.Lock()


def argv_parser(port_default, ip_default):
    # создаем парсер командной строки
    argv_pars = ArgumentParser()
    # создаем аргументы парсера - порт
    argv_pars.add_argument('-p', default=port_default, type=int, nargs='?')
    # создаем аргумент парсера ip адресс
    argv_pars.add_argument('-a', default=ip_default, nargs='?')
    # передаем парсеру параметры командной строки
    IP_and_port = argv_pars.parse_args(sys.argv[1:])
    listen_port = IP_and_port.p
    listen_ip_addr = IP_and_port.a
    return listen_ip_addr, listen_port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()

    # ip = Host()

    def __init__(self, listen_ip_addr, listen_port, database):
        self.port = listen_port
        self.ip = listen_ip_addr
        self.database = database

        # словарь 'зарегистрированных' пользователей и их сокетов
        self.names_clients = dict()
        # список клиентов ожидающих сообщения
        self.listen_socks = list()
        self.clients_list = list()
        self.messages_list = list()
        super().__init__()

    def init_socket(self):
        sock_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_1.bind((self.ip, self.port))
        # для тестирования метакласса
        # sock_1.connect()
        sock_1.settimeout(0.5)
        self.sock = sock_1
        self.sock.listen()

    def handler_messages(self, message, listen_socks):
        '''
        Функция проверяет есть ли на сервере клиент, которому отправляется сообщение
        :param message: словарь сообщения
        :param names_clients: словарь зарегистрированных пользователей и их сокетов
        :param listen_socks: список клиентов ожидающих сообщения
        :return:
        '''
        if message[DESTINATION] in self.names_clients and self.names_clients[
            message[DESTINATION]] in listen_socks:
            send_mesages(self.names_clients[message[DESTINATION]], message)
            log.info(
                f'Отправлено сообщение пользователю - {message[DESTINATION]} от - {message[SENDER]} ')
        elif message[DESTINATION] in self.names_clients and self.names_clients[
            message[DESTINATION]] not in listen_socks:
            log.error(
                f'Соединение с {self.names_clients[message[DESTINATION]]} потеряно')
            raise ConnectionError
        else:
            log.error(
                f'Отправка сообщения незарегистрированому пользователю невозможна. Пользователь{message[DESTINATION]} - не зарегистрирован на сервере')

    def handler_client_messages(self, messages, client):
        global new_connect
        # проверка если сообщение о присутствии принимаем и отвечаем
        if ACTION in messages and messages[
            ACTION] == GREETINGS and TIME in messages and USER in messages:
            if messages[USER][ACCOUNT_NAME] not in self.names_clients.keys():
                # если клиента нет в словаре добавляем его имя и сокет
                self.names_clients[messages[USER][ACCOUNT_NAME]] = client

                ip, port = client.getpeername()
                self.database.user_login(messages[USER][ACCOUNT_NAME], ip, port)
                send_mesages(client, RESPONSE_200)
                with conflag_lock:
                    new_connect = True
                log.info(
                    'Клиент- %(account_name)s подключился к серверу(отправил корректный запрос)',
                    messages[USER])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя занято'
                send_mesages(client, response)
                self.clients_list.remove(client)
                client.close()
            return
        elif ACTION in messages and messages[
            ACTION] == MESSAGE and TIME in messages and MESSAGE_TEXT in messages and SENDER in messages and DESTINATION and \
                self.names_clients[messages[SENDER]] == client:
            self.messages_list.append(messages)
            self.database.handler_message(messages[SENDER],
                                          messages[DESTINATION])
            return
        elif ACTION in messages and messages[
            ACTION] == EXIT and ACCOUNT_NAME in messages and self.names_clients[
            messages[ACCOUNT_NAME]] == client:
            self.database.user_logout(messages[ACCOUNT_NAME])
            self.clients_list.remove(self.names_clients[messages[ACCOUNT_NAME]])
            self.names_clients[messages[ACCOUNT_NAME]].close()
            del self.names_clients[messages[ACCOUNT_NAME]]
            with conflag_lock:
                new_connect = True
            return
        elif ACTION in messages and messages[
            ACTION] == GET_CONTACTS and USER in messages and self.names_clients[
            messages[USER]] == client:
            response = RESPONSE_200
            response[LIST_INFO] = self.database.get_contacts(messages[USER])
            send_mesages(client, response)
        elif ACTION in messages and messages[
            ACTION] == ADD_CONTACT and ACCOUNT_NAME in messages and USER in messages and \
                self.names_clients[messages[USER]] == client:
            self.database.add_contact(messages[USER], messages[ACCOUNT_NAME])
            send_mesages(client, RESPONSE_200)
        elif ACTION in messages and messages[
            ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in messages and USER in messages and \
                self.names_clients[messages[USER]] == client:
            self.database.remove_contact(messages[USER], messages[ACCOUNT_NAME])
            send_mesages(client, RESPONSE_200)
        elif ACTION in messages and messages[
            ACTION] == USERS_REQUEST and ACCOUNT_NAME in messages and \
                self.names_clients[messages[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in
                                   self.database.users_list()]
            send_mesages(client, response)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен'
            send_mesages(client, response)
            log.error('Клиент отправил некорректный запрос на подключение')
            return

    def print_help(self):
        print('''
        Список команд:
            users - список "зарегистрированных" пользователей
            active - список пользователей онлайн
            loginhistory - история входов пользователя 
            help - вывести подсказки
            exit - завершить работу сервера
        ''')

    def user_interaction(self):
        print('Сервер запущен ')
        self.print_help()
        while True:
            command = input('Введите команду:  ')
            if command == 'users':
                print('Список "зарегистрированных" пользователей')
                for user in self.database.users_list():
                    print(f'Имя пользователя: {user[0]}, последний вход '
                          f'{user[1].hour}:{user[1].minute}  '
                          f'{user[1].day}-{user[1].month}-{user[1].year}')
            elif command == 'active':
                print('Список пользователей онлайн')
                for user in self.database.active_users_list():
                    print(
                        f" Имя пользователя: {user[0]}, адрес {user[1]}:{user[2]}")
            elif command == 'loginhistory':
                name_user = input(
                    'Введите имя пользователя,для просмотра истории его входов,'
                    'нажмите enter чтобы посмотреть историю всех пользователей: ')
                for history in self.database.login_history(name_user):
                    print(f'Имя пользователя: {history[0]}, адрес:'
                          f' {history[1]}{history[2]}, последний вход:'
                          f'{history[3].hour}:{history[3].minute}  '
                          f'{history[3].day}-{history[3].month}-{history[3].year}')
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                print('Завершение работы сервера')
                sys.exit(1)
            else:
                print('Несуществующая команда, для просмотра доступных '
                      'программ введите "help"')

    def run(self):
        self.init_socket()
        while True:
            try:
                # accept - принимает запрос на соединение
                client, client_ip_addr = self.sock.accept()
            except OSError:
                pass
            else:
                log.info(f'Установлено соединение с {client_ip_addr}')
                self.clients_list.append(client)
            # создаем переменные для принятия данных от select
            recv_lst = list()
            send_lst = list()
            err_lst = list()
            try:
                if self.clients_list:
                    # recv_lst-список клиентов, отправивших сообщение,send_lst- список клиентов,ждущих сообщение
                    recv_lst, send_lst, err_lst = select(self.clients_list,
                                                         self.clients_list, [],
                                                         0)
            except OSError:
                pass

            if recv_lst:
                for client_with_messages in recv_lst:
                    try:
                        self.handler_client_messages(
                            get_messages(client_with_messages),
                            client_with_messages)
                    except(OSError):
                        # getpeername() - возвращает удаленный Ip-addr
                        log.info(f'Клиент {client_with_messages.getpeername()} '
                                 f'отключился от сервера.')
                        for name in self.names_clients:
                            if self.names_clients[name] == client_with_messages:
                                self.database.user_logout(name)
                                del self.names_clients[name]
                                break
                        self.clients_list.remove(client_with_messages)

            for i in self.messages_list:
                try:
                    self.handler_messages(i, send_lst)
                except Exception:
                    log.info(f'Клиент {i[DESTINATION]} отключился')
                    self.clients_list.remove(self.names_clients[i[DESTINATION]])
                    self.database.user_logout(i[DESTINATION])
                    del self.names_clients[i[DESTINATION]]
            self.messages_list.clear()


def main():
    config = ConfigParser()
    directory = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{directory}/{"server.ini"}')

    # ip, port = argv_parser()
    ip, port = argv_parser(config['SETTINGS']['default_port'],
                           config['SETTINGS']['listen_address'])
    # print(ip,port)
    database = ServerDatabase(os.path.join(config['SETTINGS']['database_path'],
                                           config['SETTINGS']['database_file']))
    server = Server(ip, port, database)
    server.daemon = True

    server.start()
    log.info(
        f'Запущен сервер, порт для подключения:{port}, IP-адресс для подключения: {ip}')
    # server.user_interaction()
    app = QApplication(sys.argv)
    window = GeneralWindow()
    window.statusBar().showMessage('Сервер запущен')
    window.active_user_list.setModel(gui_create_model_tabel(database))
    window.active_user_list.resizeColumnsToContents()
    window.active_user_list.resizeRowsToContents()

    def update_data_list():
        global new_connect
        if new_connect:
            window.active_user_list.setModel(gui_create_model_tabel(database))
            window.active_user_list.resizeColumnsToContents()
            window.active_user_list.resizeRowsToContents()
            with conflag_lock:
                new_connect = False  # else:  #     print('Нет')

    def show_statics_users():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.table_history.setModel(gui_create_stat_model(database))
        stat_window.table_history.resizeColumnsToContents()
        stat_window.table_history.resizeRowsToContents()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.path_database.insert(config['SETTINGS']['database_path'])
        config_window.db_file_name_input.insert(
            config['SETTINGS']['database_file'])
        config_window.port.insert(config['SETTINGS']['default_port'])
        config_window.ip.insert(config['SETTINGS']['listen_address'])
        config_window.save_button.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['database_path'] = config_window.path_database.text()
        print(config['SETTINGS']['database_path'])
        config['SETTINGS'][
            'database_file'] = config_window.db_file_name_input.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['listen_address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = str(port)
                # print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK',
                                        'Настройки успешно сохранены')
            else:
                message.warning(config_window, 'Ошибка',
                                'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(update_data_list)
    timer.start(1000)
    window.refresh_list.triggered.connect(update_data_list)
    window.show_history_client.triggered.connect(show_statics_users)
    window.config_server.triggered.connect(server_config)
    app.setWindowIcon(QIcon('favicon.png'))
    app.exec_()


if __name__ == '__main__':
    main()
