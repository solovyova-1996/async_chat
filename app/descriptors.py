# Реализовать дескриптор для класса серверного сокета, а в нем — проверку номера
# порта. Это должно быть целое число (>=0).
# Значение порта по умолчанию равняется 7777.
# Дескриптор надо создать в отдельном классе.
# Его экземпляр добавить в пределах класса серверного сокета. Номер порта передается
# в экземпляр дескриптора при запуске сервера.
import sys
from logging import getLogger

from config import server_log_config

log = getLogger('server')


class Port:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            # print('Error')
            log.critical(
                f'Номер порта не удовлетворяет условию -от 1024 до 65535.Переданный порт- {value}.Process finished with exit code 1')
            sys.exit(1)
        instance.__dict__[self.name] = value

if __name__ == '__main__':

    class NewCl:
        port = ServerPort()

    a = NewCl()
    a.port = 89999
    print(a.port)