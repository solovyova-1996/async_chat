import unittest
from collections import namedtuple
from chat.server import get_port, get_addr

Args = namedtuple('Args', ['host', 'port'])
args = Args(host='', port=7777)

class TestServer(unittest.TestCase):
    def setUp(self):
        print("Начало тестирования пакета server")

    def tearDown(self):
        print("Завершение тестирования пакета server")

    def test_get_port(self):
        result = get_port(args)
        self.assertEqual(result, 7777, f"Тест не пройден, ожидалось {7777}, а пришло {result}")

    def test_get_addr(self):
        result = get_addr(args)
        self.assertEqual(result, "", f"Тест не пройден, ожидалось {''}, а пришло {result}")
