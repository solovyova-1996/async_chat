import sys
import threading
from logging import getLogger
from argparse import ArgumentParser
import socket
from select import select

from general.utils import get_messages, send_mesages
from general.variables import ACTION, GREETINGS, TIME, USER, ACCOUNT_NAME, \
    ERROR, DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER, \
    RESPONSE_200, RESPONSE_400, DESTINATION, EXIT

from config import server_log_config
from decorators_log import log_func
from metaclasses import ServerVerifier
from server_database import ServerDatabase

log = getLogger('server')
from descriptors import Port, Host


def argv_parser():
    # создаем парсер командной строки
    argv_pars = ArgumentParser()
    # создаем аргументы парсера - порт
    argv_pars.add_argument('-p', default=DEFAULT_PORT, type=int)
    # создаем аргумент парсера ip адресс
    argv_pars.add_argument('-a', default='127.0.0.1')
    # передаем парсеру параметры командной строки
    IP_and_port = argv_pars.parse_args(sys.argv[1:])
    listen_port = IP_and_port.p
    listen_ip_addr = IP_and_port.a
    return listen_ip_addr, listen_port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()
    ip = Host()

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
        self.sock.listen(MAX_CONNECTIONS)


    def handler_messages(self, message, names_clients, listen_socks):
        '''
        Функция проверяет есть ли на сервере клиент, которому отправляется сообщение
        :param message: словарь сообщения
        :param names_clients: словарь зарегистрированных пользователей и их сокетов
        :param listen_socks: список клиентов ожидающих сообщения
        :return:
        '''
        if message[DESTINATION] in names_clients and names_clients[
            message[DESTINATION]] in listen_socks:
            send_mesages(names_clients[message[DESTINATION]], message)
            log.info(
                f'Отправлено сообщение пользователю - {message[DESTINATION]} от - {message[SENDER]} ')
        elif message[DESTINATION] in names_clients and names_clients[
            message[DESTINATION]] not in listen_socks:
            log.error(
                f'Соединение с {names_clients[message[DESTINATION]]} потеряно')
            raise ConnectionError
        else:
            log.error(
                f'Отправка сообщения незарегистрированому пользователю невозможна. Пользователь{message[DESTINATION]} - не зарегистрирован на сервере')

    def handler_client_messages(self, messages, messages_list, client,
                                clients_list, names_clients):
        # проверка если сообщение о присутствии принимаем и отвечаем
        if ACTION in messages and messages[
            ACTION] == GREETINGS and TIME in messages and USER in messages:
            if messages[USER][ACCOUNT_NAME] not in names_clients.keys():
                # если клиента нет в словаре добавляем его имя и сокет
                names_clients[messages[USER][ACCOUNT_NAME]] = client
                send_mesages(client, RESPONSE_200)
                ip, port = client.getpeername()
                self.database.user_login(messages[USER][ACCOUNT_NAME], ip, port)
                log.info(
                    'Клиент- %(account_name)s подключился к серверу(отправил корректный запрос)',
                    messages[USER])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя занято'
                send_mesages(client, response)
                clients_list.remove(client)
                client.close()
            return
        elif ACTION in messages and messages[
            ACTION] == MESSAGE and TIME in messages and MESSAGE_TEXT in messages and SENDER in messages and DESTINATION:
            messages_list.append(messages)
            return
        elif ACTION in messages and messages[
            ACTION] == EXIT and ACCOUNT_NAME in messages:
            self.database.user_logout(messages[ACCOUNT_NAME])
            clients_list.remove(names_clients[messages[ACCOUNT_NAME]])
            names_clients[messages[ACCOUNT_NAME]].close()
            del names_clients[messages[ACCOUNT_NAME]]
            return
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
                            self.messages_list, client_with_messages,
                            self.clients_list, self.names_clients)
                    except:
                        # getpeername() - возвращает удаленный Ip-addr
                        log.info(f'Клиент {client_with_messages.getpeername()} '
                                 f'отключился от сервера.')
                        self.clients_list.remove(client_with_messages)

            for i in self.messages_list:
                try:
                    self.handler_messages(i, self.names_clients, send_lst)
                except Exception:
                    log.info(f'Клиент {i[DESTINATION]} отключился')
                    self.clients_list.remove(self.names_clients[i[DESTINATION]])
                    del self.names_clients[i[DESTINATION]]
            self.messages_list.clear()


def main():
    ip, port = argv_parser()
    database = ServerDatabase()
    server = Server(ip, port, database)
    server.daemon = True

    log.info(
        f'Запущен сервер, порт для подключения:{port}, IP-адресс для подключения: {ip}')
    server.start()
    server.user_interaction()


if __name__ == '__main__':
    main()
