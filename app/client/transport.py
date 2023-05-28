import json
import logging
import socket
import sys
import threading
from time import time, sleep

from PyQt5.QtCore import QObject, pyqtSignal


from app.general.utils import send_mesages, get_messages
from app.general.variables import ACTION, USERS_REQUEST, TIME, ACCOUNT_NAME, \
    RESPONSE, LIST_INFO, GET_CONTACTS, USER, GREETINGS, ERROR, MESSAGE, SENDER, \
    DESTINATION, MESSAGE_TEXT, ADD_CONTACT, REMOVE_CONTACT, EXIT

from app.errors import ServerError

sys.path.append('../')
logger = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.transport = None
        self.connection_init(port, ip)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            logger.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        self.running = True

    def connection_init(self, port, ip):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)
        connected = False
        for num in range(5):
            logger.info(f'Попытка подключения №{num + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            sleep(1)
        if not connected:
            logger.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')
        logger.debug('Установлено соединение с сервером')
        try:
            with socket_lock:
                send_mesages(self.transport, self.create_presence())
                self.handler_server_answer(get_messages(self.transport))
        except (OSError, json.JSONDecodeError):
            logger.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')
        logger.info('Соединение с сервером успешно установлено.')

    def handler_server_answer(self, message):
        logger.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                logger.debug(
                    f'Принят неизвестный код подтверждения {message[RESPONSE]}')
        elif ACTION in message and message[
            ACTION] == MESSAGE and SENDER in message and DESTINATION in message and MESSAGE_TEXT in message and \
                message[DESTINATION] == self.username:
            logger.debug(
                f'Получено сообщение от пользователя {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in',
                                       message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def add_contact(self, contact):
        logger.debug(f'Создание контакта {contact}')
        request = {ACTION: ADD_CONTACT, TIME: time(), USER: self.username,
                   ACCOUNT_NAME: contact}
        # print(request)
        with socket_lock:
            send_mesages(self.transport, request)
            self.handler_server_answer(get_messages(self.transport))

    def remove_contacts(self, contact):
        logger.debug(f'Удаление контакта {contact}')
        request = {ACTION: REMOVE_CONTACT, TIME: time(), USER: self.username,
                   ACCOUNT_NAME: contact}
        with socket_lock:
            send_mesages(self.transport, request)
            self.handler_server_answer(get_messages(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = {ACTION: EXIT, TIME: time(), ACCOUNT_NAME: self.username}
        with socket_lock:
            try:
                send_mesages(self.transport, message)
            except OSError:
                pass
        logger.debug('Транспорт завершает работу.')
        sleep(0.5)

    def create_presence(self):
        out = {ACTION: GREETINGS, TIME: time(),
               USER: {ACCOUNT_NAME: self.username}}
        logger.debug(
            f'Сформировано {GREETINGS} сообщение для пользователя {self.username}')
        return out

    def user_list_update(self):
        logger.debug(f'Запрос списка известных пользователей {self.username}')
        request = {ACTION: USERS_REQUEST, TIME: time(),
                   ACCOUNT_NAME: self.username}
        with socket_lock:
            send_mesages(self.transport, request)
            answer = get_messages(self.transport)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            self.database.add_users(answer[LIST_INFO])
        else:
            logger.error('Не удалось обновить список известных пользователей.')

    def contacts_list_update(self):
        logger.debug(f'Запрос контакт листа для пользователся {self.name}')
        request = {ACTION: GET_CONTACTS, TIME: time(), USER: self.username}
        logger.debug(f'Сформирован запрос {request}')
        with socket_lock:
            send_mesages(self.transport, request)
            answer = get_messages(self.transport)
        logger.debug(f'Получен ответ {answer}')
        if RESPONSE in answer and answer[RESPONSE] == 202:
            for contact in answer[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            logger.error('Не удалось обновить список контактов.')

    def send_message(self, to, message):
        message_dict = {ACTION: MESSAGE, SENDER: self.username, DESTINATION: to,
                        TIME: time(), MESSAGE_TEXT: message}
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        with socket_lock:
            print('вошли')
            send_mesages(self.transport, message_dict)
            self.handler_server_answer(get_messages(self.transport))
            print(get_messages(self.transport))
            logger.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        logger.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_messages(self.transport)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (
                ConnectionError, ConnectionAbortedError, ConnectionResetError,
                json.JSONDecodeError, TypeError):
                    logger.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f'Принято сообщение с сервера: {message}')
                    self.handler_server_answer(message)
                finally:
                    self.transport.settimeout(5)
