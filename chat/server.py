# Функции сервера:
# принимает сообщение клиента;
# формирует ответ клиенту;
# отправляет ответ клиенту;
# имеет параметры
# командной строки: -p <port> — TCP-порт для работы (по умолчанию использует 7776); -a
# <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
import argparse
from socket import *

from chat.log import log_server_deco
from log import log_server

parser = argparse.ArgumentParser()
host = parser.add_argument('--host', type=str, default='')
port = parser.add_argument('--port', type=int, default=7776)

args = parser.parse_args()


@log_server_deco
def get_port(args):
    log_server.info('вызов функции get_port')
    return args.port


@log_server_deco
def get_addr(args):
    log_server.info('вызов функции get_addr')
    return args.host


def server_socket():
    port = get_port(args)
    addr = get_addr(args)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((addr, port))
    sock.listen()
    while True:
        client, addr = sock.accept()
        data = client.recv(100000)
        log_server.info(f"Сообщение от сервера: {data.decode('utf-8')} было отправлено клиентом: {addr} ")
        message = 'Привет клиент'
        client.send(message.encode('utf-8'))
        client.close()


if __name__ == '__main__':
    try:
        server_socket()
    except Exception as ex:
        log_server.critical(f"Непредвиденная ошибка {ex}")
