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
# по умолчанию 7777.


from socket import *
import sys


def get_port():
    try:
        return int(sys.argv[sys.argv.index('-p') + 1])
    except ValueError:
        return 7777


def get_addr():
    try:
        return sys.argv[sys.argv.index('-a') + 1]
    except ValueError:
        return "localhost"


def get_message():
    try:
        return sys.argv[sys.argv.index('-m') + 1]
    except ValueError:
        return "Пустое сообщение от клиента"


def send_messages(sock, message, addr, port):
    sock.connect((addr, port))
    sock.send(message.encode('utf-8'))
    return sock.recv(1000000)


def client():
    port = get_port()
    addr = get_addr()
    message = get_message()
    sock = socket(AF_INET, SOCK_STREAM)
    data = send_messages(sock, message, addr, port)
    print('Сообщение от сервера: ', data.decode('utf-8'), ', длиной ', len(data), 'байт')
    sock.close()


if __name__ == "__main__":
    client()
