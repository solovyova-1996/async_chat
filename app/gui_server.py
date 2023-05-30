from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, qApp, \
    QLabel, QTableView, QDialog, QPushButton, QLineEdit, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt
import sys


def gui_create_model_tabel(database):
    active_users_list = database.active_users_list()
    # print(active_users_list)
    model_table = QStandardItemModel()
    model_table.setHorizontalHeaderLabels(
        ['Пользователь', 'IP-адрес', 'Порт', 'Время подключения', ])

    for row in active_users_list:
        user, ip, port, time = row
        # создание элементов
        user = QStandardItem(user)
        # user.setStyleSheet('background-color:blak;color:white')
        ip = QStandardItem(ip)
        port = QStandardItem(str(port))
        time = QStandardItem(str(time.replace(microsecond=0)))
        # запрет на редактирование элементов
        user.setEditable(False)
        ip.setEditable(False)
        port.setEditable(False)
        time.setEditable(False)
        model_table.appendRow([user, ip, port, time])
    return model_table


def gui_create_stat_model(db):
    history_list = db.message_history()
    table = QStandardItemModel()
    table.setHorizontalHeaderLabels(
        ['Пользователь', 'Последний вход', 'Исходящие сообщения',
         'Входящие сообщения'])
    for row in history_list:
        user, last_login, sent, recv = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_login = QStandardItem(str(last_login.replace(microsecond=0)))
        last_login.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        recv = QStandardItem(str(recv))
        recv.setEditable(False)
        table.appendRow([user, last_login, sent, recv])
    return table


class GeneralWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # создание заголовка главного окна
        self.setWindowTitle('Сервер месенджера')
        # фиксированные размеры окна
        self.setFixedSize(800, 600)

        # содание кнопки выхода, добавление горячих клавиш для выхода
        exitButton = QAction(QIcon('exitButton.png'), 'Выход', self)
        exitButton.setShortcut('Ctr+Q')
        # отображение подсказки в строке состояния при наведении
        exitButton.setStatusTip('Выход из приложения')
        exitButton.triggered.connect(qApp.quit)

        self.refresh_list = QAction('Обновить список', self)
        self.refresh_list.setStatusTip('Обновить список активных пользователей')
        self.config_server = QAction('Настройки сервера', self)
        self.config_server.setStatusTip('Просмотр и изменение настроек сервера')
        self.show_history_client = QAction('История пользователей', self)
        self.show_history_client.setStatusTip(
            'Просмотр статистики пользователей')

        self.statusBar().showMessage('Загрузка...')

        # создание панели инструментов
        self.toolbar = self.addToolBar('Toolbar')
        # добавление стилей
        self.toolbar.setStyleSheet('background-color:blak;color:white')
        # добавление кнопок на панель задач
        self.toolbar.addAction(self.refresh_list)
        self.toolbar.addAction(self.config_server)
        self.toolbar.addAction(self.show_history_client)
        self.toolbar.addAction(exitButton)

        self.label = QLabel('Список подключенных клиентов ', self)
        self.label.setFixedSize(240, 15)
        # положение по x y
        self.label.move(10, 40)

        self.active_user_list = QTableView(self)
        self.active_user_list.setFixedSize(780, 400)
        self.active_user_list.move(10, 55)

        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setWindowTitle('Статистика пользователей')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнопка закрытия окна
        self.close_button = QPushButton('&Закрыть окно', self)
        self.close_button.setStyleSheet('background-color:red;color:white')
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # таблица статистики пользователей
        self.table_history = QTableView(self)
        self.table_history.move(10, 10)
        self.table_history.setFixedSize(580, 620)
        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setWindowTitle('Настройки сервера')
        self.setFixedSize(365, 260)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # надпись (путь до базы данных)
        self.path_database_label = QLabel('Путь до базы данных', self)
        self.path_database_label.move(10, 10)
        self.path_database_label.setFixedSize(240, 15)

        # путь до базы данных
        self.path_database = QLineEdit(self)
        self.path_database.move(10, 30)
        self.path_database.setFixedSize(250, 20)
        self.path_database.setReadOnly(True)

        # кнопка для выбора файла базы данных
        # self.select_path_database = QPushButton('Выбрать файл',self)
        self.select_path_database = QPushButton(QIcon('path.png'),
                                                'Выбрать файл', self)
        self.select_path_database.move(275, 28)
        font = QFont()
        font.setPointSize(6)
        self.select_path_database.setFont(font)

        def open_file_explorer():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.path_database.insert(path)

        # поле с названием файла базы данных
        self.select_path_database.clicked.connect(open_file_explorer)
        self.db_file_name = QLabel('Имя базы данных: ', self)
        self.db_file_name.move(10, 68)
        self.db_file_name.setFixedSize(180, 15)

        # Поле для ввода имени файла базы данных
        self.db_file_name_input = QLineEdit(self)
        self.db_file_name_input.move(110, 65)
        self.db_file_name_input.setFixedSize(240, 20)

        # поле с ip адресом
        self.ip_addr_label = QLabel('С какого IP принимаем соединения: ', self)
        self.ip_addr_label.move(10, 150)
        self.ip_addr_label.setFixedSize(180, 15)

        # поле с напоминанием о пустом поле ip адреса.
        self.ip_addr_note = QLabel(
            '*оставьте это поле пустым, чтобы принимать соединения с любых адресов',
            self)
        self.ip_addr_note.move(10, 160)
        self.ip_addr_note.setFixedSize(360, 30)
        font = QFont()
        font.setPointSize(7)
        self.ip_addr_note.setFont(font)

        # поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 145)
        self.ip.setFixedSize(150, 20)

        # кнопка для сохранения настроек сервера
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(190, 220)
        self.save_button.setStyleSheet('background-color:blue;color:white')

        # кнопка для закрытия окна
        self.close_btn = QPushButton('Закрыть', self)
        self.close_btn.move(275, 220)
        self.close_btn.setStyleSheet('background-color:red;color:white')
        self.close_btn.clicked.connect(self.close)

        # поле с номером порта
        self.port_label = QLabel('Номер порта для соединений: ', self)
        self.port_label.move(10, 110)
        self.port_label.setFixedSize(180, 15)

        # поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(170, 108)
        self.port.setFixedSize(180, 20)
        self.show()


if __name__ == '__main__':
    # создание приложения
    app = QApplication(sys.argv)
    # создание главного окна
    window = GeneralWindow()
    test_list = QStandardItemModel(window)
    test_list.setHorizontalHeaderLabels(
        ['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])

    test_list.appendRow(
        [QStandardItem('1'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow(
        [QStandardItem('4'), QStandardItem('5'), QStandardItem('6')])
    window.active_user_list.setModel(test_list)
    window.active_user_list.resizeColumnsToContents()
    history_window = HistoryWindow()

    config_window = ConfigWindow()
    sys.exit(app.exec_())
