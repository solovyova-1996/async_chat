from sqlalchemy import Table, Column, create_engine, MetaData, Integer, String, \
    DateTime, ForeignKey
from sqlalchemy.orm import mapper, Session, sessionmaker
from datetime import datetime

database_name = 'sqlite:///server_database.db3'


class ServerDatabase:
    # классы для внесения данных в таблицу
    class Users(object):
        def __init__(self, name):
            self.id = None
            self.name = name
            self.last_login = datetime.now()

        def __repr__(self):
            return f'< User({self.id},{self.name},{self.last_login}) >'

    class UsersActive(object):
        def __init__(self, id_user, ip, port, login_time):
            self.id = None
            self.user = id_user
            self.ip = ip
            self.port = port
            self.login_time = login_time

        def __repr__(self):
            return f'< UserActive({self.user},{self.ip}:{self.port},{self.login_time})>'

    class LoginHistory(object):
        def __init__(self, id_user, ip, port, date_time):
            self.id = None
            self.user_name = id_user
            self.ip = ip
            self.port = port
            self.date_time = date_time

        def __repr__(self):
            return f'< LoginHistory({self.user_name},{self.ip}:{self.port},{self.date_time})>'

    class UsersContacts(object):
        def __init__(self, user, contact):
            self.user = user
            self.contact = contact
            self.id = None

    class UsersHistory(object):
        def __init__(self, user):
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # создание базы данных
        self.database = create_engine(f'sqlite:///{path}', echo=False,
                                      pool_recycle=7200,
                                      connect_args={'check_same_thread': False})
        # для создания таблиц типа migrate , makemigrations
        self.metadata = MetaData()
        # создание сессии для внесения изменений в бд
        Session = sessionmaker(bind=self.database)
        self.session = Session()
        # создание таблиц
        self.users_table = Table('users', self.metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('name', String),
                                 Column('last_login', DateTime))

        self.active_users_table = Table('users_active', self.metadata,
                                        Column('id', Integer, primary_key=True),
                                        Column('user', ForeignKey('users.id'),
                                               unique=True),
                                        Column('port', Integer),
                                        Column('ip', String),
                                        Column('login_time', DateTime))

        self.history_login_user_table = Table('login_history', self.metadata,
                                              Column('id', Integer,
                                                     primary_key=True),
                                              Column('user_name',
                                                     ForeignKey('users.id')),
                                              Column('ip', String),
                                              Column('port', Integer),
                                              Column('date_time', DateTime))
        self.user_contacts_table = Table('user-contacts', self.metadata,
                                         Column('id', Integer,
                                                primary_key=True),
                                         Column('user', ForeignKey('users.id')),
                                         Column('contact',
                                                ForeignKey('users.id')))
        self.user_history_table = Table('users-history', self.metadata,
                                        Column('id', Integer, primary_key=True),
                                        Column('user', ForeignKey('users.id')),
                                        Column('sent', Integer),
                                        Column('accepted', Integer))
        # создание всех таблиц
        self.metadata.create_all(self.database)

        # соединение таблицы и класса для ее заполнения
        self.mapper_user = mapper(self.Users, self.users_table)
        self.mapper_user_active = mapper(self.UsersActive,
                                         self.active_users_table)
        self.mapper_login_history = mapper(self.LoginHistory,
                                           self.history_login_user_table)
        self.mapper_user_contacts = mapper(self.UsersContacts,
                                           self.user_contacts_table)
        self.mapper_users_history = mapper(self.UsersHistory,
                                           self.user_history_table)

        #   удаление записей в таблице активных пользователей(так как необходимо соблюдать уникальность записей)
        self.session.query(self.UsersActive).delete()
        self.session.commit()

    def user_login(self, name_user, ip, port):
        # print(f'Пользователь: {name_user} ({ip}:{port}) - вошёл в систему')
        result = self.session.query(self.Users).filter_by(name=name_user)
        # print(result)

        if result.count():
            user = result.first()
            user.last_login = datetime.now()  # self.session.add(user)
        else:
            user = self.Users(name_user)
            self.session.add(user)
            self.session.commit()
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        new_active_user = self.UsersActive(user.id, ip, port, datetime.now())
        self.session.add(new_active_user)
        new_login_history = self.LoginHistory(user.id, ip, port, datetime.now())
        self.session.add(new_login_history)
        self.session.commit()

    def user_logout(self, user):
        user = self.session.query(self.Users).filter_by(name=user)
        user = user.first()
        user_delete = self.session.query(self.UsersActive).filter_by(
            user=user.id).delete()
        self.session.commit()

    def users_list(self):
        return self.session.query(self.Users.name, self.Users.last_login).all()

    def active_users_list(self):
        return self.session.query(self.Users.name, self.UsersActive.ip,
                                  self.UsersActive.port,
                                  self.UsersActive.login_time).join(
            self.Users).all()

    def login_history(self, username=None):
        login_history_lst = self.session.query(self.Users.name,
                                               self.LoginHistory.ip,
                                               self.LoginHistory.port,
                                               self.LoginHistory.date_time).join(
            self.Users)
        if username:
            return login_history_lst.filter(self.Users.name == username).all()
        return login_history_lst.all()

    def handler_message(self, sender, recipient):
        # id отправителя
        sender = self.session.query(self.Users).filter_by(
            name=sender).first().id
        # id получателя
        recipient = self.session.query(self.Users).filter_by(
            name=recipient).first().id
        # print(sender)
        # print(recipient)
        sender_value = self.session.query(self.UsersHistory).filter_by(
            user=sender).first()
        sender_value.sent += 1
        recipient_value = self.session.query(self.UsersHistory).filter_by(
            user=recipient).first()
        recipient_value.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        # Функция добавляет в таблицу контактов запись
        # (осуществляется проверка на наличие подобной записи в таблице, если запись есть запись пропускается)
        user = self.session.query(self.Users).filter_by(name=user).first()
        contact = self.session.query(self.Users).filter_by(
            name=contact).first()
        if not contact or self.session.query(self.UsersContacts).filter_by(
                user=user.id, contact=contact.id).count():
            return
        contact_new = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_new)
        self.session.commit()

    def remove_contacts(self, user, contact):
        user = self.session.query(self.Users).filter_by(name=user).firtst()
        contact = self.session.query(self.Users).filter_by(
            name=contact).firtst()
        if not contact:
            return
        print(self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id).delete())
        self.session.commit()

    def message_history(self):
        query = self.session.query(self.Users.name, self.Users.last_login,
                                   self.UsersHistory.sent,
                                   self.UsersHistory.accepted).join(self.Users)

        return query.all()

    def get_contacts(self, username):
        user = self.session.query(self.Users).filter_by(name=username).one()
        query = self.session.query(self.UsersContacts,
                                   self.Users.name).filter_by(
            user=user.id).join(self.Users,
                               self.UsersContacts.contact == self.Users.id)
        return [contact[1] for contact in query.all()]


if __name__ == '__main__':
    server = ServerDatabase()
    server.user_login('user', 'localhost', 8000)
    server.user_login('user1', 'localhost', 8000)
    server.user_login('user2', 'localhost', 8000)
    server.user_login('user3', 'localhost', 8000)
    print(server.users_list())
    print(server.active_users_list())
    server.user_logout('user1')
    print(server.active_users_list())
    server.handler_message('user', 'user2')
    print(server.message_history())
