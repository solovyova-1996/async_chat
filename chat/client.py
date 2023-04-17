# Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):
# клиент отправляет запрос серверу;
# сервер отвечает соответствующим кодом результата.
# Клиент и сервер должны быть реализованы в виде отдельных скриптов,
# содержащих соответствующие функции.
# Функции клиента:
# сформировать presence-сообщение;
# отправить сообщение серверу;
# получить ответ сервера;
# разобрать сообщение сервера;
# параметры командной строки скрипта client.py <addr> [<port>]: addr — ip-адрес сервера; port — tcp-порт на сервере,
# по умолчанию 3233.


from socket import *
import argparse
from log import log_client

parser = argparse.ArgumentParser()
host = parser.add_argument('--host', type=str, default='localhost')
port = parser.add_argument('--port', type=int, default=3233)
message = parser.add_argument('--message', type=str, default='Пустое сообщение от клиента')
args = parser.parse_args()


def get_port(args):
    log_client.info('вызов функции get_port')
    return args.port


def get_addr(args):
    log_client.info('вызов функции get_addr')
    return args.host


def get_message(args):
    log_client.info('вызов функции get_message')
    return args.message


def send_messages(sock, message, addr, port):
    sock.connect((addr, port))
    sock.send(message.encode('utf-8'))
    return sock.recv(1000000)


def client():
    log_client.info('запуск клиента')
    port = get_port(args)
    addr = get_addr(args)
    message = get_message(args)
    sock = socket(AF_INET, SOCK_STREAM)
    data = send_messages(sock, message, addr, port)
    log_client.info(f"Сообщение от сервера: {data.decode('utf-8')} длиной: {len(data)}  байт")
    sock.close()


if __name__ == "__main__":
    try:
        client()
    except Exception as ex:
        log_client.critical(f"Непредвиденная ошибка {ex}")
