from sqlalchemy import Table, Column, create_engine, MetaData, Integer, String, \
    DateTime, ForeignKey
from sqlalchemy.orm import mapper, Session
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

    def __init__(self):
        # создание базы данных
        self.database = create_engine(database_name, echo=False,
                                      pool_recycle=7200)
        # для создания таблиц типа migrate , makemigrations
        self.metadata = MetaData()
        # создание сессии для внесения изменений в бд
        self.session = Session(self.database)
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

        # создание всех таблиц
        self.metadata.create_all(self.database)
        # соединение таблицы и класса для ее заполнения
        self.mapper_user = mapper(self.Users, self.users_table)
        self.mapper_user_active = mapper(self.UsersActive,
                                         self.active_users_table)
        self.mapper_login_history = mapper(self.LoginHistory,
                                           self.history_login_user_table)

    def user_login(self, name_user, ip, port):
        # print(f'Пользователь: {name_user} ({ip}:{port}) - вошёл в систему')
        result = self.session.query(self.Users).filter_by(name=name_user)
        # print(result)

        if result.count():
            user = result.first()
            user.last_login = datetime.now()
            self.session.add(user)
        else:
            user = self.Users(name_user)
            self.session.add(user)
        self.session.commit()
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









####################пример для себя##################
# имя базы данных
# database_name='sqlite:///server_database.db3'
# # создание базы данных
# database = create_engine(database_name,echo=False,pool_recycle=7200)
# # создание сессии для работы с базой данных, чтобы можно было сохранять данные в таблицы
# session = Session(database)
#
# metadata = MetaData() # для создания таблиц типа migrate , makemigrations
# # создание таблицы
# users_table = Table('users',metadata,
#     Column('id',Integer,primary_key=True),
#     Column('name',String),
#     Column('last_login',DateTime)
# )
# # класс для внесения данных в таблицу
# class User(object):
#     def __init__(self,name):
#         self.id = None
#         self.name = name
#         self.last_login = datetime.now()
#     def __repr__(self):
#         return f'< User({self.id},{self.name},{self.last_login}) >'
# # создание всех таблиц
# metadata.create_all(database)
# # соединение таблицы и класса для ее заполнения
# mapper_user=mapper(User,users_table)
# # создание пользователя
# user_1 = User('даша')
# # добавление пользователя в таблицу
# session.add(user_1)
# # сохранение данных в базу
# session.commit()
# print(session.query(User).all())
#
