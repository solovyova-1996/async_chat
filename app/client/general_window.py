import logging

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox

from client.add_contact import AddContactDialog
from client.del_contact import DelContactDialog
from client.general_window_conf import Ui_MainClientWindow
from errors import ServerError

logger = logging.getLogger('client')


class ClientGeneralWindow(QMainWindow):
    def __init__(self, database, transport):
        super().__init__()
        # база данных
        self.database = database
        # сокет
        self.transport = transport
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        # кнопка выхода
        self.ui.menu_exit.triggered.connect(qApp.exit)

        # кнопка отправки сообщения
        self.ui.btn_send.clicked.connect(self.send_message)

        # добавление контакта
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        # удаление контакта
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        # обработка двойного клика по списку контактов
        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        '''
        деактивация полей ввода
        :return:
        '''
        self.ui.label_new_message.setText(
            'Для выбора получателя дважды кликните на нем в окне контактов.')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()
        # поле ввода сообщение и кнопка отправки сообщения неактивны до выбора получателя
        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

    def history_list_update(self):
        '''
        заполнение истории сообщений(входящие и исходящие сообщения разным цветом и в разных сторонах)
        :return:
        '''
        lst = sorted(self.database.get_history(self.current_chat),
                     key=lambda item: item[3])
        # print(lst)
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        self.history_model.clear()
        length = len(lst)
        start_index = 0
        if length > 20:
            start_index = length - 20
        for i in range(start_index, length):
            item = lst[i]
            if item[1] == 'in':
                message = QStandardItem(
                    f'Входящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(255, 213, 213)))
                message.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(message)
            else:
                message = QStandardItem(
                    f'Исходящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                message.setEditable(False)
                message.setTextAlignment(Qt.AlignRight)
                message.setBackground((QBrush(QColor(204, 255, 204))))
                self.history_model.appendRow(message)
            self.ui.list_messages.scrollToBottom()

    def clients_list_update(self):
        '''
        Функция обновляющая список контактов
        :return:
        '''
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def select_active_user(self):
        '''
        обработчик двойного клика по контакту
        :return:
        '''
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        '''
        Функция установки активного собеседника,заполняет историю сообщений
        с выбранным пользователемделает активными поле ввода и кнопку
        для отпарвки сообщения
        :return:
        '''
        self.ui.label_new_message.setText(
            f'Введите сообщенние для {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        # заполнение истории сообщений с выбранным пользователем
        self.history_list_update()

    def add_contact_window(self):
        '''
        Добавление контакта
        :return:
        '''
        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.btn_ok.clicked.connect(
            lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        '''
        Функция - обработчик добавления, сообщает серверу, обновляет таблицу и список контактов
        :param item:
        :return:
        '''
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        '''
        Добавляет контакт в базу данных
        :param new_contact:
        :return:
        '''
        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка сервера', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка',
                                       'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Успешно добавлен контакт {new_contact}')
            self.messages.information(self, 'Успех',
                                      'Контакт успешно добавлен.')

    def delete_contact_window(self):
        '''Удаление контакта'''
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(
            lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        '''
        обработчик удаления контакта, сообщает на сервер об удалении и обновляет список контактов
        :param item:
        :return:
        '''
        selected = item.selector.currentText()
        try:
            self.transport.remove_contact(selected)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка сервера', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка',
                                       'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            logger.info(f'Успешно удалён контакт {selected}')
            self.messages.information(self, 'Успех', 'Контакт успешно удалён.')
            item.close()
            # Если удалён активный пользователь, то деактивируем поля ввода.
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        '''Отправка сообщения пользователю'''
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        # print(self.current_chat)
        if not message_text:
            return
        try:
            self.transport.send_message(self.current_chat, message_text)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка', err.text)
        except OSError as err:
            # print(err)
            if err.errno:
                self.messages.critical(self, 'Ошибка',
                                       'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Ошибка',
                                   'Потеряно соединение с сервером!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            logger.debug(
                f'Отправлено сообщение для {self.current_chat}: {message_text}')

    @pyqtSlot(str)
    def message(self, sender):
        '''Слот приема нового сообщения'''
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Проверим есть ли такой пользователь у нас в контактах:
            if self.database.check_contact(sender):
                # Если есть, спрашиваем и желании открыть с ним чат и открываем при желании
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}, открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # Раз нету,спрашиваем хотим ли добавить юзера в контакты.
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}.\n Данного пользователя нет в вашем контакт-листе.\n Добавить в контакты и открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        '''Потеря соединения, выдает сообщение об ошибке, завершает работу приложения'''
        self.messages.warning(self, 'Сбой соединения',
                              'Потеряно соединение с сервером. ')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)
