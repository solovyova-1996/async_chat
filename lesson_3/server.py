# Функции сервера:
# принимает сообщение клиента;
# формирует ответ клиенту;
# отправляет ответ клиенту;
# имеет параметры
# командной строки: -p <port> — TCP-порт для работы (по умолчанию использует 7777); -a
# <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).

from socket import *
import sys


def server_socket():
    try:
        port = int(sys.argv[sys.argv.index('-p')+1])
    except IndexError:
        port = 7777
    try:
        addr = sys.argv[sys.argv.index('-a')+1]
    except IndexError:
        addr = ""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((addr, port))
    sock.listen()
    while True:
        client, addr = sock.accept()
        data = client.recv(100000)
        print("Сообщение: ", data.decode('utf-8'), "было отправлено клиентом:", addr)
        message = 'Привет клиент'
        client.send(message.encode('utf-8'))
        client.close()


if __name__ == '__main__':
    server_socket()
