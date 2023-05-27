from client1 import create_greetings, handler_response_from_server
from general.variables import ACTION, TIME, GREETINGS, ACCOUNT_NAME, USER, \
    GUEST, RESPONSE, ERROR

from unittest import TestCase


class TestClient(TestCase):
    def setUp(self):
        # парметры для теста test_create_greetings
        self.time_for_test = 0
        self.expected_result = {ACTION: GREETINGS, TIME: self.time_for_test,
                                USER: {ACCOUNT_NAME: GUEST}}
        # параметры для тестов test_handler_response_from_server_ok, test_handler_response_from_server_error
        self.messages_from_server_ok = {RESPONSE: 200}
        self.messages_from_server_error = {RESPONSE: 400, ERROR: 'Bad Request'}
        self.correct_answer_from_function_ok = 'Код ответа:200 - "ОК"'
        self.correct_answer_from_function_error = 'Код ответа:400 : Bad Request'

    def tearDown(self) -> None:
        del self.expected_result, self.correct_answer_from_function_error, \
            self.correct_answer_from_function_ok, self.messages_from_server_error,\
            self.messages_from_server_ok, self.time_for_test

    def test_create_greetings(self):
        test_data = create_greetings()
        test_data[TIME] = self.time_for_test
        self.assertEqual(test_data, self.expected_result)

    def test_handler_response_from_server_ok(self):
        self.assertEqual(
            handler_response_from_server(self.messages_from_server_ok),
            self.correct_answer_from_function_ok)

    def test_handler_response_from_server_error(self):
        self.assertEqual(
            handler_response_from_server(self.messages_from_server_error),
            self.correct_answer_from_function_error)

    def test_no_response(self):
        self.assertRaises(ValueError, handler_response_from_server,
                          {ERROR: 'Bad Request'})
