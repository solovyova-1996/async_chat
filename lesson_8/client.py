import json
import sys
from argparse import ArgumentParser
from json import JSONDecodeError
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from time import time, sleep
import threading

from errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError
from general.utils import send_mesages, get_messages
from decorators_log import log_func, LogClass
from general.variables import ACTION, GREETINGS, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE_TEXT, MESSAGE, \
    SENDER, EXIT, DESTINATION

from config import client_log_config

log = getLogger('client')


@log_func
def print_info_help():
    print('''
Привет!!! ты находишься в консольном мессенжере
Команды:
message - отправка сообщения
help - вывести подсказки
exit - выйти

    ''')


def create_exit_message(account_name):
    '''
    Создает сообщение о выходе из мессенжера
    :param account_name:
    :return:
    '''
    return {ACTION: EXIT, TIME: time(), ACCOUNT_NAME: account_name}


@log_func
def user_interaction(sock, username):
    print_info_help()
    while True:
        command = input('Введите команду:  \n')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_info_help()
        elif command == 'exit':
            message_exit = create_exit_message(username)
            send_mesages(sock, message_exit)
            param = {'username': username}
            log.info('Пользователь %(username)d вышел из мессенжера', param)
            sleep(0.5)
            break
        else:
            print(
                'Введенная команда недоступна. Введите help для просмотра доступных комманд')


@log_func
def handler_message_from_users(sock, username):
    while True:
        try:
            message = get_messages(sock)
            if ACTION in message and message[
                ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message and DESTINATION in message and \
                    message[DESTINATION] == username:
                print(
                    f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                log.info(
                    f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                log.error(
                    f'От сервера получено некорректное сообщение : {message}')
        except IncorrectDataRecivedError:
            log.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            log.critical(f'Потеряно соединение с сервером.')
            break


@log_func
def create_message(sock, account_name='Guest'):
    to_user = input(
        'Введите имя пользователя, которому хотите отправить сообщение: ')
    message = input('Введите сообщение: ')

    message_create = {ACTION: MESSAGE, TIME: time(), SENDER: account_name,
                      DESTINATION: to_user, MESSAGE_TEXT: message}
    log.debug(f'Создано сообщение {message_create}')
    try:
        send_mesages(sock, message_create)
        log.info(f'Отправлено сообщение({message}) пользователю:{to_user}')
    except:
        log.critical('Потеряно соединение с сервером')
        sys.exit(1)


@log_func
def create_greetings(account_name='Guest'):
    # генерация запроса о присутствии клиента
    return {ACTION: GREETINGS, TIME: time(), USER: {ACCOUNT_NAME: account_name}}


@LogClass()
def handler_response_from_server(message):
    # print(message)
    log.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


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
    IP_and_port_and_mode = argv_pars.parse_args(sys.argv[1:])
    server_port = IP_and_port_and_mode.port
    server_ip_addr = IP_and_port_and_mode.addr
    client_name = IP_and_port_and_mode.name

    if server_port < 1024 or server_port > 65535:
        param = {'server_port': server_port}
        log.critical(
            'Номер порта не удовлетворяет условию -от 1024 до 65535.Переданный порт- %(server_port)d.Process finished with exit code 1',
            param)
        sys.exit(1)

    return server_ip_addr, server_port, client_name


def main():
    server_ip_addr, server_port, client_name = argv_parser()
    print(client_name)
    if not client_name:
        client_name = input('Введите имя поьзователя')
    log.info(
        f'Запущен клиент с ip-адресом{server_ip_addr}, порт:{server_port}, с именем:{client_name}')
    try:
        # создаем сетевой потоковый сокет
        sock_1 = socket(AF_INET, SOCK_STREAM)
        # устанавливаем соединение с сокетом
        # print(server_ip_addr, server_port)
        sock_1.connect((server_ip_addr, server_port))
        # создаем сообщение о присутствии клмента на сервере
        messages_to_server = create_greetings(client_name)

        # кодируем данные в байты и отправляем на сервер
        send_mesages(sock_1, messages_to_server)
        answer = handler_response_from_server(get_messages(sock_1))
        log.info(
            f'Установлено соединение с сервером. Ответ от сервера {answer}')
        print('Соединение с сервером установлено')
    except json.JSONDecodeError:
        log.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        log.error(
            f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        log.error(
            f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        log.critical(
            f'Не удалось подключиться к серверу {server_ip_addr}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно,
        # создаем 2 потока- один принимает сообщение, другой - отправляет
        # поток принимающий сообщений
        receive_mess = threading.Thread(target=handler_message_from_users,
            args=(sock_1, client_name))
        # receive_mess.daemon = True
        receive_mess.start()
        send_mess = threading.Thread(target=user_interaction,
                                     args=(sock_1, client_name))
        # send_mess.daemon=True
        send_mess.start()
        log.debug('Потоки запущены')


if __name__ == '__main__':
    main()
