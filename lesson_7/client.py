from socket import *

host_port = ('localhost', 7776)


def client():
    """
    client launch function that sends a message to the server
    :return:
    """
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect(host_port)
        while True:
            msg = input('Введите "stop" для выхода'
                        '\nНапишите сообщение : ')
            if msg == 'stop':
                break
            sock.send(msg.encode('utf-8'))
            data = sock.recv(1024).decode('utf-8')
            print(f'Ответ от сервера: {data}')


if __name__ == '__main__':
    client()
