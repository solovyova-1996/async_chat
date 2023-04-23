import select
from socket import socket, AF_INET, SOCK_STREAM


def message_read(r_clients, all_clients):
    """
    Function that creates a dictionary {sock:message}
    :param r_clients: list of clients who wrote the message
    :param all_clients: list of all clients
    :return:dict
    """
    responses = {}
    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            responses[sock] = data
        except:
            print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
            all_clients.remove(sock)
    return responses


def answer_write(requests, w_clients, all_clients):
    """
    Function that sends an echo message in lowercase to the client
    :param requests: dictionary {sock:message}
    :param w_clients: list of clients waiting for a response
    :param all_clients: list of all clients
    :return:
    """
    for sock in w_clients:
        if sock in requests:
            try:
                resp = requests[sock].encode('utf-8')
                sock.send(resp.lower())
            except:
                print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
                sock.close()
                all_clients.remove(sock)


def start_server():
    """
    Server start function
    :return:
    """
    address = ('localhost', 7776)
    clients = []
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(5)
    s.settimeout(0.2)
    while True:
        try:
            conn, addr = s.accept()
        except OSError as e:
            print(f"Возникла ошибка :{e}")
            pass
        else:
            print(f"Получен запрос на соединение от {str(addr)}")
            clients.append(conn)  # добавление в список клиентов сокета
        finally:
            read = []
            write = []
            try:
                read, write, error = select.select(clients, clients, [], 9)
            except:
                pass
            requests = message_read(read, clients)
            if requests:
                answer_write(requests, write, clients)


if __name__ == "__main__":
    print('Эхо-сервер запущен!')
    start_server()
