import unittest
from socket import socket, AF_INET, SOCK_STREAM

from lesson_3.client import get_port, get_addr, get_message, send_messages


class TestClient(unittest.TestCase):
    def setUp(self):
        print("Начало тестирования пакета client")

    def tearDown(self):
        print("Завершение тестирования пакета client")

    def test_get_port(self):
        result = get_port()
        self.assertEqual(result, 7777, f"Тест не пройден, ожидалось {7777}, а пришло {result}")

    def test_get_addr(self):
        result = get_addr()
        self.assertEqual(result, "localhost", f"Тест не пройден, ожидалось {'localhost'}, а пришло {result}")

    def test_get_message(self):
        result = get_message()
        self.assertEqual(result, "Пустое сообщение от клиента",
                         f"Тест не пройден, ожидалось {'Пустое сообщение от клиента'}, а пришло {result}")

    def test_send_messages(self):
        port = get_port()
        addr = get_addr()
        message = get_message()
        sock = socket(AF_INET, SOCK_STREAM)
        result = send_messages(sock, message, addr, port)
        self.assertEqual(result.decode('utf-8'), "Привет клиент",
                         f"Тест не пройден, ожидалось {'Привет клиент'}, а пришло {result.decode('utf-8')}")
