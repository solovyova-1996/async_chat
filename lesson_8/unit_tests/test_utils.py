from json import dumps
from unittest import TestCase

from general.utils import send_mesages, get_messages
from general.variables import ENCODING, ACTION, GREETINGS, TIME, USER, \
    ACCOUNT_NAME, GUEST, RESPONSE, ERROR


class ImitationSocket:
    def __init__(self, test_data):
        self.test_data = test_data
        self.bytes_mess = None
        self.accept_mess = None

    def send(self, message_to_send):
        # переданное при создании сокета сообщение - test_data сериализуем в строку json-формата
        json_mess = dumps(self.test_data)
        # кодируем сообщение в байты
        self.bytes_mess = json_mess.encode(ENCODING)
        # охраняем в атрибуте класса accept_mess сообщение которое нужно отправить в сокет
        self.accept_mess = message_to_send

    def recv(self,param):
        # переданное при создании сокета сообщение - test_data сериализуем в строку json-формата
        json_mess = dumps(self.test_data)
        # возращаем сообщение в байтах
        return json_mess.encode(ENCODING)


class TestUtils(TestCase):
    def setUp(self) -> None:
        self.test_time = 0
        self.mess_send = {ACTION: GREETINGS, TIME: self.test_time,
                          USER: {ACCOUNT_NAME: GUEST}}
        self.mess_from_server_ok = {RESPONSE: 200}
        self.mess_from_server_error = {RESPONSE: 400, ERROR: 'Bad Request'}

    def tearDown(self) -> None:
        pass

    def test_send_messages(self):
        # создаем иммитацию сокета и передаем сообщение
        imitation_socket = ImitationSocket(self.mess_send)
        # в функцию отправки сообщения передаем созданный сокет и сообщение
        send_mesages(imitation_socket, self.mess_send)
        # сравниваем сообщение в байтах
        self.assertEqual(imitation_socket.bytes_mess,
                         imitation_socket.accept_mess)
        with self.assertRaises(Exception):
            send_mesages(imitation_socket, imitation_socket)
    def test_get_messages(self):
        # создаем сокет и передаем ему сообщение от сервера с ответом ok
        imitation_socket_ok = ImitationSocket(self.mess_from_server_ok)
        # создаем сокет и передаем ему сообщение от сервера с ответом error
        imitation_socket_error = ImitationSocket(self.mess_from_server_error)
        self.assertEqual(get_messages(imitation_socket_ok),self.mess_from_server_ok)
        self.assertEqual(get_messages(imitation_socket_error),self.mess_from_server_error)
