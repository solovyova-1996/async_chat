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


def client():
    try:
        port = int(sys.argv[sys.argv.index('-p')+1])
    except ValueError:
        port = 7777
    try:
        addr = sys.argv[sys.argv.index('-a')+1]
    except ValueError:
        addr = "localhost"
    try:
        message = sys.argv[sys.argv.index('-m')+1]
    except ValueError:
        message = "Пустое сообщение от клиента"
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((addr, port))
    sock.send(message.encode('utf-8'))
    data = sock.recv(1000000)
    print('Сообщение от сервера: ', data.decode('utf-8'), ', длиной ', len(data), 'байт')
    sock.close()


if __name__ == "__main__":
    client()
