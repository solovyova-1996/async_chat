import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        attributes = list()
        methods = list()
        for func in clsdict:
            try:
                gen = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in gen:
                    if i.opname == 'LOAD_METHOD':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)

        # print(f'Функции(методы) использованные в классе Server: {methods}')
        # print(f'Атрибуты класса Server: {attributes}')
        if 'connect' in methods:
            raise TypeError('Недопустимый метод "connect" в серверном сокете')
        if not ('AF_INET' in attributes and 'SOCK_STREAM' in attributes):
            raise TypeError(
                'Неверное создание сокета, при создании сокета необходимо '
                'указать параметры: socket.AF_INET, socket.SOCK_STREAM')
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):

    def __init__(self, clsname, bases, clsdict):
        methods = list()
        attributes = list()
        for func in clsdict:
            try:
                gen = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in gen:
                    if i.opname == 'LOAD_METHOD':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)

        # print(f'Функции(методы) использованные в классе Client: {methods}')
        # print(f'Атрибуты класса Client: {attributes}')

        if not ('AF_INET' in attributes and 'SOCK_STREAM' in attributes):
            raise TypeError(
                'Неверное создание сокета, при создании сокета необходимо '
                'указать параметры: socket.AF_INET, socket.SOCK_STREAM')
        if 'accept' in methods or 'listen' in methods:
            raise TypeError(
                'Методы accept и listen недопустимы в клиентском сокете')
        super().__init__(clsname, bases, clsdict)
