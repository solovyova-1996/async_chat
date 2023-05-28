import os
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, \
    Text, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ClientDatabase:
    # классы для внесения данных в таблицы
    class KnowUsers(object):
        def __init__(self, user):
            self.id = None
            self.username = user

    class MessagesHistory(object):
        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.now()

    class Contacts(object):
        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client{name}.db3'
        # создание базы данных
        self.database = create_engine(
            f'sqlite:///{os.path.join(path, filename)}', echo=False,
            pool_recycle=7200, connect_args={'check_same_thread': False})

        # необходимо для создания таблиц
        self.metadata = MetaData()

        # создание таблиц
        users = Table('know_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String))
        history = Table('messages_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('contact', String),
                        Column('direction', String),
                        Column('message', Text),
                        Column('date', DateTime))
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True))

        # создание всех таблиц
        self.metadata.create_all(self.database)

        # соединение таблицы и класса для ее заполнения
        mapper(self.KnowUsers, users)
        mapper(self.MessagesHistory, history)
        mapper(self.Contacts, contacts)

        # создание сессии для внесения изменения в базу данных
        Session = sessionmaker(bind=self.database)
        self.session = Session()

        # удаление записей из таблицы Contacts так как значения там должны быть уникальными
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        '''
        Добавление контакта в таблицу контактов
        :param contact: имя контакта
        :return:
        '''
        if not self.session.query(self.Contacts).filter_by(
                name=contact).count():
            new_contact = self.Contacts(contact)
            self.session.add(new_contact)
            self.session.commit()

    def del_contact(self, contact):
        '''
        Удаление контакта из таблицы контактов
        :param contact: имя контакта
        :return:
        '''
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list):
        '''
        Добавление нескольких контактов в таблицу известных пользователей(удаление всех пользователей из таблицы перед добавлением)
        :param users_list: список с именами пользователей
        :return:
        '''
        self.session.query(self.KnowUsers).delete()
        for user in users_list:
            new_user = self.KnowUsers(user)
            self.session.add(new_user)
        self.session.commit()

    def save_message(self, contact, direction, message):
        '''
        Сохранение сообщения в таблицу истории сообщений
        :param contact:имя контакта
        :param direction: in или out
        :param message: тескт сообщения
        :return:
        '''
        new_message = self.MessagesHistory(contact, direction, message)
        self.session.add(new_message)
        self.session.commit()

    def get_contacts(self):
        '''
        Возврат списка всех контактов
        :return: список с именами всех контактов
        '''
        return [contact[0] for contact in
                self.session.query(self.Contacts.name).all()]

    def get_users(self):
        '''
        Возврат списка имен всех известных пользователей
        :return: список с именами всех известных пользователей
        '''
        return [user[0] for user in
                self.session.query(self.KnowUsers.username).all()]

    def check_user(self, user):
        '''
        Проверка на наличие пользователя в таблице известных пользователей
        :param user: имя пользователя
        :return: True or False
        '''
        if self.session.query(self.KnowUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        '''
        Проверка наличия контакта в таблице контактов
        :param contact: имя контакта
        :return: True or False
        '''
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        '''
        Возвращает список кортежей с историей сообщений контакта
        :param contact: имя контакта(с которым нужно показать историю сообщений)
        :return: список кортежей (имя контакта, in or out,текст сообщения,дата)
        '''
        query = self.session.query(self.MessagesHistory).filter_by(
            contact=contact)
        return [(
            history_row.contact, history_row.direction, history_row.message,
            history_row.date) for history_row in query.all()]


if __name__ == '__main__':
    # создание тестовой базы данных
    database_test = ClientDatabase('test_db')

    # тестовые данные
    users = ['user1', 'user2', 'user3', 'user4']
    contacts = ['contacts1', 'contacts2', 'contacts3', 'contacts4']

    # наполнение таблицы известных пользователей тестовыми данными
    database_test.add_users(users)
    # наполнение таблицы контактов тестовыми данными
    for contact in contacts:
        database_test.add_contact(contact)
    # создание записей в таблице истории сообщений
    database_test.save_message('contact1', 'in', 'Привет contact1 ')
    database_test.save_message('contact2', 'out', 'Привет contact2 ')

    # напечатать список известных пользователей
    print(f'Известные пользователи: \n{database_test.get_users()}')
    # напечатать список контактов
    print(f'Контакты: \n{database_test.get_contacts()}')
    # проверка существует ли пользователе
    print(
        f'Существует ли пользователь user1 ?- {database_test.check_user("user1")}')
    # проверка существует ли контакт
    print(
        f'Существует ли контакт contact5 ?- {database_test.check_contact("contact1")}')
    # просмотр истории сообщений для contact1
    print(database_test.get_history('contact1'))
