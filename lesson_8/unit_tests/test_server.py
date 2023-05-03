from time import time
from unittest import TestCase

from general.variables import RESPONSE, ERROR, ACTION, GREETINGS, TIME, USER, \
    ACCOUNT_NAME, GUEST
from server import handler_client_messages


class TestServer(TestCase):
    def setUp(self, account_name=None) -> None:
        self.response_ok = {RESPONSE: 200}
        self.response_error = {RESPONSE: 400, ERROR: 'Bad Request'}
        self.dict_no_action = {TIME: time(), USER: {ACCOUNT_NAME: account_name}}
        self.dict_no_time = {ACTION: GREETINGS,
                             USER: {ACCOUNT_NAME: account_name}}
        self.dict_no_user = {ACTION: GREETINGS, TIME: time()}

    def tearDown(self) -> None:
        pass

    def test_handler_client_messages_no_action(self):
        self.assertEqual(handler_client_messages(self.dict_no_action),
                         self.response_error)

    def test_handler_client_messages_no_time(self):
        self.assertEqual(handler_client_messages(self.dict_no_time),
                         self.response_error,
                         'В функцию test_handler_client_messages передан словарь, не содержащий обязательный ключ - time')

    def test_handler_client_messages_no_user(self):
        self.assertNotEqual(handler_client_messages(self.dict_no_user),
                            self.response_ok)

    def test_handler_client_messages_wrong_action(self):
        self.assertEqual(handler_client_messages(
            {ACTION: 'GREETINGS', TIME: time(), USER: {ACCOUNT_NAME: GUEST}}),
            self.response_error)

    def test_handler_client_messages_wrong_account(self):
        self.assertEqual(handler_client_messages(
            {ACTION: GREETINGS, TIME: time(), USER: {ACCOUNT_NAME: 'daria'}}),
            self.response_error)

    def test_handler_client_messages_correct(self):
        self.assertEqual(handler_client_messages(
            {ACTION: GREETINGS, TIME: time(), USER: {ACCOUNT_NAME: GUEST}}),
                         self.response_ok)
