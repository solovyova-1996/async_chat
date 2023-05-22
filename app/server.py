import sys
import time
from logging import getLogger
# from socket import socket, AF_INET, SOCK_STREAM
from argparse import ArgumentParser
import socket
from select import select

from general.utils import get_messages, send_mesages
from general.variables import ACTION, GREETINGS, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, PORT_ARGV, DEFAULT_PORT, IP_ARGV, MAX_CONNECTIONS, MESSAGE, \
    MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT

from config import server_log_config
from decorators_log import log_func
from metaclasses import ServerVerifier

log = getLogger('server')
from descriptors import Port


def argv_parser():
    # создаем парсер командной строки
    argv_pars = ArgumentParser()
    # создаем аргументы парсера - порт
    argv_pars.add_argument('-p', default=DEFAULT_PORT, type=int)
    # создаем аргумент парсера ip адресс
    argv_pars.add_argument('-a', default='')
    # передаем парсеру параметры командной строки
    IP_and_port = argv_pars.parse_args(sys.argv[1:])
    listen_port = IP_and_port.p
    listen_ip_addr = IP_and_port.a
    return listen_ip_addr, listen_port


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_ip_addr, listen_port):
        self.port = listen_port
        self.ip = listen_ip_addr

        # словарь 'зарегистрированных' пользователей и их сокетов
        self.names_clients = dict()
        # список клиентов ожидающих сообщения
        self.listen_socks = list()
        self.clients_list = list()
        self.messages_list = list()

    def init_socket(self):
        sock_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_1.bind((self.ip, self.port))
        # для тестирования метакласса
        # sock_1.connect()
        sock_1.settimeout(0.5)
        self.sock = sock_1
        self.sock.listen(MAX_CONNECTIONS)
        print('Сервер запущен ')


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
        # print(clients_list)
        # print(names_clients)
        if ACTION in messages and messages[
            ACTION] == GREETINGS and TIME in messages and USER in messages:
            if messages[USER][ACCOUNT_NAME] not in names_clients.keys():
                # если клиента нет в словаре добавляем его имя и сокет
                names_clients[messages[USER][ACCOUNT_NAME]] = client
                send_mesages(client, RESPONSE_200)
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

    def main(self):
        while True:
            # accept - принимает запрос на соединение
            try:
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
    server = Server(ip, port)
    server_sock = server.init_socket()
    log.info(
        f'Запущен сервер, порт для подключения:{port}, IP-адресс для подключения: {ip}')
    server.main()


if __name__ == '__main__':
    main()

# def handler_messages(message, names_clients, listen_socks):
#     '''
#     Функция проверяет есть ли на сервере клиент, которому отправляется сообщение
#     :param message: словарь сообщения
#     :param names_clients: словарь зарегистрированных пользователей и их сокетов
#     :param listen_socks: список клиентов ожидающих сообщения
#     :return:
#     '''
#     if message[DESTINATION] in names_clients and names_clients[
#         message[DESTINATION]] in listen_socks:
#         send_mesages(names_clients[message[DESTINATION]], message)
#         log.info(
#             f'Отправлено сообщение пользователю - {message[DESTINATION]} от - {message[SENDER]} ')
#     elif message[DESTINATION] in names_clients and names_clients[
#         message[DESTINATION]] not in listen_socks:
#         log.error(
#             f'Соединение с {names_clients[message[DESTINATION]]} потеряно')
#         raise ConnectionError
#     else:
#         log.error(
#             f'Отправка сообщения незарегистрированому пользователю невозможна. Пользователь{message[DESTINATION]} - не зарегистрирован на сервере')
#
#
# @log_func
# def handler_client_messages(messages, messages_list, client, clients_list,
#                             names_clients):
#     # проверка если сообщение о присутствии принимаем и отвечаем
#     # print(clients_list)
#     # print(names_clients)
#     if ACTION in messages and messages[
#         ACTION] == GREETINGS and TIME in messages and USER in messages:
#         if messages[USER][ACCOUNT_NAME] not in names_clients.keys():
#             # если клиента нет в словаре добавляем его имя и сокет
#             names_clients[messages[USER][ACCOUNT_NAME]] = client
#             send_mesages(client, RESPONSE_200)
#             log.info(
#                 'Клиент- %(account_name)s подключился к серверу(отправил корректный запрос)',
#                 messages[USER])
#         else:
#             response = RESPONSE_400
#             response[ERROR] = 'Имя пользователя занято'
#             send_mesages(client, response)
#             clients_list.remove(client)
#             client.close()
#         return
#     elif ACTION in messages and messages[
#         ACTION] == MESSAGE and TIME in messages and MESSAGE_TEXT in messages and SENDER in messages and DESTINATION:
#         messages_list.append(messages)
#         return
#     elif ACTION in messages and messages[
#         ACTION] == EXIT and ACCOUNT_NAME in messages:
#         clients_list.remove(names_clients[messages[ACCOUNT_NAME]])
#         names_clients[messages[ACCOUNT_NAME]].close()
#         del names_clients[messages[ACCOUNT_NAME]]
#         return
#     else:
#         response = RESPONSE_400
#         response[ERROR] = 'Запрос некорректен'
#         send_mesages(client, response)
#         log.error('Клиент отправил некорректный запрос на подключение')
#         return


# def main():
#     # print(argv_parser())
#     listen_ip_addr, listen_port = argv_parser()
#     log.info(
#         f'Запущен сервер, порт для подключения:{listen_port}, IP-адресс для подключения: {listen_ip_addr}')
#
#     # создаем сокет AF_INET-сетевой, SOCK_STREAM - тип сокета потоковый
#     sock_1 = socket(AF_INET, SOCK_STREAM)
#     # привязываем сокет к ip адресу и порту машины
#     sock_1.bind((listen_ip_addr, listen_port))
#     sock_1.settimeout(0.5)
#     clients_list = list()
#     messages_list = list()
#     # словарь с клиентами и их сокетами
#     names_clients = dict()
#     # сигнализируем о готовности принимать соединение MAX_CONNECTIONS - количество одновременно обслуживаемых запросов
#     sock_1.listen(MAX_CONNECTIONS)
#     print('Сервер запущен')
#     while True:
#         # accept - принимает запрос на соединение
#         try:
#             client, client_ip_addr = sock_1.accept()
#         except OSError:
#             pass
#         else:
#             log.info(f'Установлено соединение с {client_ip_addr}')
#             clients_list.append(client)
#         # создаем переменные для принятия данных от select
#         recv_lst = list()
#         send_lst = list()
#         err_lst = list()
#         try:
#             if clients_list:
#                 # recv_lst-список клиентов, отправивших сообщение,send_lst- список клиентов,ждущих сообщение
#                 recv_lst, send_lst, err_lst = select(clients_list, clients_list,
#                                                      [], 0)
#         except OSError:
#             pass
#
#         if recv_lst:
#             for client_with_messages in recv_lst:
#                 try:
#                     handler_client_messages(get_messages(client_with_messages),
#                                             messages_list, client_with_messages,
#                                             clients_list, names_clients)
#                 except:
#                     # getpeername() - возвращает удаленный Ip-addr
#                     log.info(f'Клиент {client_with_messages.getpeername()} '
#                              f'отключился от сервера.')
#                     clients_list.remove(client_with_messages)
#
#         for i in messages_list:
#             try:
#                 handler_messages(i, names_clients, send_lst)
#             except Exception:
#                 log.info(f'Клиент {i[DESTINATION]} отключился')
#                 clients_list.remove(names_clients[i[DESTINATION]])
#                 del names_clients[i[DESTINATION]]
#         messages_list.clear()
