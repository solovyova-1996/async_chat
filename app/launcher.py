import subprocess
import random
import time

process_list = list()


def get_number_name():
    return f'{random.getrandbits(4)}'


while True:
    command = input('Выберите действие: q - выход, '
                    's - запустить сервер, c - запустить клиентов, x - закрыть все окна: ')
    if command == 'q':
        break
    elif command == 'c':
        try:
            count_client = int(input(
                'Введите количество клиентов, которое необходимо запустить:  '))
        except ValueError:
            try:
                count_client = int(
                    input('Вы ввели не число.Попробуйте еще раз:  '))
            except ValueError:
                count_client = 5


        for i in range(count_client):
            name = get_number_name()
            process_list.append(subprocess.Popen(f'python client_1.py -n USER{name}',creationflags=subprocess.CREATE_NEW_CONSOLE))
            # process_list.append(subprocess.Popen(f'python client_1.py ',creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif command == 's':

        process = subprocess.Popen('python server.py',
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
        process_list.append(process)
    elif command == 'x':
        while process_list:
            process_kill = process_list.pop()
            process_kill.kill()
