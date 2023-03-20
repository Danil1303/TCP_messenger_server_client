import sys
import socket
from time import localtime, strftime, sleep
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPlainTextEdit, QPushButton, \
    QMessageBox


class TCPConnect(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.connection_type = None
        self.current_socket = None
        self.address = None
        self.port = None
        self.user_name = None
        self.max_connections_to_server = 10
        self.connected_to_server_users = []

        self.thread_server_connection = None
        self.thread_input = None

        self.setWindowTitle('TCP connect')
        self.setFixedSize(175, 90)

        self.button_create_server = QPushButton(self)
        self.button_create_server.setText('Режим работы: сервер')
        self.button_create_server.setGeometry(10, 10, 155, 30)
        self.button_create_server.clicked.connect(self.create_server)

        self.button_create_client = QPushButton(self)
        self.button_create_client.setText('Режим работы: клиент')
        self.button_create_client.setGeometry(10, 50, 155, 30)
        self.button_create_client.clicked.connect(self.create_client)

        self.button_start_menu = QPushButton(self)
        self.button_start_menu.setText('Вернуться в главное меню')
        self.button_start_menu.setVisible(False)
        self.button_start_menu.clicked.connect(self.start_menu)

        self.label_address = QLabel(self)
        self.label_address.setText('Адрес сервера:')
        self.label_address.move(10, 5)
        self.label_address.setVisible(False)
        self.line_edit_address = QLineEdit(self)
        self.line_edit_address.setGeometry(155, 5, 135, 30)
        self.line_edit_address.setVisible(False)

        self.label_port = QLabel(self)
        self.label_port.setText('Порт сервера:')
        self.label_port.move(10, 45)
        self.label_port.adjustSize()
        self.label_port.setVisible(False)
        self.line_edit_port = QLineEdit(self)
        self.line_edit_port.setGeometry(155, 40, 135, 30)
        self.line_edit_port.setVisible(False)

        self.label_user_name = QLabel(self)
        self.label_user_name.setText('Имя пользователя:')
        self.label_user_name.move(10, 80)
        self.label_user_name.adjustSize()
        self.label_user_name.setVisible(False)
        self.line_edit_user_name = QLineEdit(self)
        self.line_edit_user_name.setGeometry(155, 75, 135, 30)
        self.line_edit_user_name.setVisible(False)

        self.button_connection = QPushButton(self)
        self.button_connection.setVisible(False)
        self.button_connection.clicked.connect(self.connection)

        self.button_disconnection = QPushButton(self)
        self.button_disconnection.setGeometry(10, 300, 155, 30)
        self.button_disconnection.setVisible(False)
        self.button_disconnection.clicked.connect(self.disconnection)

        self.label_server_status = QLabel(self)
        self.label_server_status.setVisible(False)

        self.label_recipient_user_name = QLabel(self)
        self.label_recipient_user_name.setText('Адресат сообщения:')
        self.label_recipient_user_name.move(10, 160)
        self.label_recipient_user_name.adjustSize()
        self.label_recipient_user_name.setVisible(False)
        self.combo_box_recipient_user_name = QComboBox(self)
        self.combo_box_recipient_user_name.setGeometry(155, 155, 135, 30)
        self.combo_box_recipient_user_name.setVisible(False)

        self.label_send_message = QLabel(self)
        self.label_send_message.setText('Сообщение:')
        self.label_send_message.move(10, 195)
        self.label_send_message.adjustSize()
        self.label_send_message.setVisible(False)
        self.line_edit_message = QLineEdit(self)
        self.line_edit_message.setGeometry(90, 190, 200, 30)
        self.line_edit_message.setVisible(False)

        self.button_send = QPushButton(self)
        self.button_send.setText('Отправить')
        self.button_send.setGeometry(10, 225, 280, 30)
        self.button_send.setVisible(False)
        self.button_send.clicked.connect(self.send)

        self.plain_text_edit_status_report = QPlainTextEdit(self)
        self.plain_text_edit_status_report.setReadOnly(True)
        self.plain_text_edit_status_report.setVisible(False)

        self.message_box = QMessageBox(self)

        self.line_edit_address.setText('127.0.0.1')
        self.line_edit_port.setText('13000')

    def view_server_interface(self) -> None:
        self.button_create_server.setVisible(False)
        self.button_create_client.setVisible(False)
        self.setWindowTitle('Server')
        self.setFixedSize(600, 500)

        self.button_start_menu.setGeometry(10, 460, 580, 30)
        self.button_start_menu.setVisible(True)

        self.label_address.setVisible(True)
        self.line_edit_address.setVisible(True)

        self.label_port.setVisible(True)
        self.line_edit_port.setVisible(True)

        self.button_connection.setText('Создать сервер')
        self.button_connection.setGeometry(10, 75, 135, 30)
        self.button_connection.setVisible(True)
        self.button_disconnection.setText('Отключить сервер')
        self.button_disconnection.setGeometry(155, 75, 135, 30)
        self.button_disconnection.setVisible(True)
        self.button_disconnection.setEnabled(False)

        self.label_server_status.setVisible(True)
        self.label_server_status.setText('Статус:\n'
                                         'Сервер отключён')
        self.label_server_status.adjustSize()
        self.label_server_status.move(10, 110)

        self.plain_text_edit_status_report.setGeometry(10, 165, 580, 285)
        self.plain_text_edit_status_report.setVisible(True)
        self.plain_text_edit_status_report.setEnabled(False)

    def view_client_interface(self) -> None:
        self.connection_type = 'client'

        self.button_create_server.setVisible(False)
        self.button_create_client.setVisible(False)
        self.setWindowTitle('Client')
        self.setFixedSize(300, 500)

        self.button_start_menu.setGeometry(10, 460, 280, 30)
        self.button_start_menu.setVisible(True)

        self.label_address.setVisible(True)
        self.line_edit_address.setVisible(True)
        self.line_edit_address.setEnabled(True)

        self.label_port.setVisible(True)
        self.line_edit_port.setVisible(True)
        self.line_edit_port.setEnabled(True)

        self.label_user_name.setVisible(True)
        self.line_edit_user_name.setVisible(True)
        self.line_edit_user_name.setEnabled(True)

        self.button_connection.setText('Подключиться')
        self.button_connection.setGeometry(10, 110, 135, 30)
        self.button_connection.setVisible(True)
        self.button_disconnection.setText('Отключиться')
        self.button_disconnection.setGeometry(155, 110, 135, 30)
        self.button_disconnection.setVisible(True)
        self.button_disconnection.setEnabled(False)

        self.label_recipient_user_name.setVisible(True)
        self.combo_box_recipient_user_name.setVisible(True)
        self.combo_box_recipient_user_name.setEnabled(False)
        self.label_send_message.setVisible(True)
        self.line_edit_message.setVisible(True)
        self.line_edit_message.setEnabled(False)
        self.button_send.setVisible(True)
        self.button_send.setEnabled(False)

        self.plain_text_edit_status_report.setGeometry(10, 260, 280, 190)
        self.plain_text_edit_status_report.setVisible(True)
        self.plain_text_edit_status_report.setEnabled(False)

    def view_start_menu_interface(self) -> None:
        self.setWindowTitle('TCP connect')
        self.setFixedSize(175, 90)

        self.button_create_server.setVisible(True)
        self.button_create_client.setVisible(True)

        self.label_address.setVisible(False)
        self.line_edit_address.setVisible(False)

        self.label_port.setVisible(False)
        self.line_edit_port.setVisible(False)

        self.button_connection.setVisible(False)
        self.button_disconnection.setVisible(False)
        self.button_connection.setEnabled(True)
        self.button_disconnection.setEnabled(False)

        self.label_server_status.setVisible(False)

        if self.connection_type == 'server':
            self.thread_server_connection.stop()
            self.thread_server_connection = None
            self.label_server_status.setVisible(False)

        elif self.connection_type == 'client':
            if self.thread_input:
                self.thread_input.stop()
                self.thread_input = None
            self.line_edit_user_name.clear()
            self.label_user_name.setVisible(False)
            self.line_edit_user_name.setVisible(False)

            self.label_recipient_user_name.setVisible(False)
            self.combo_box_recipient_user_name.setVisible(False)
            self.label_send_message.setVisible(False)
            self.line_edit_message.setVisible(False)
            self.button_send.setVisible(False)
            self.line_edit_message.clear()

        self.plain_text_edit_status_report.setVisible(False)
        self.plain_text_edit_status_report.clear()

    def connection_mode(self) -> None:

        self.line_edit_address.setEnabled(False)
        self.line_edit_port.setEnabled(False)

        self.button_connection.setEnabled(False)
        self.button_disconnection.setEnabled(True)

        self.plain_text_edit_status_report.setEnabled(True)

        if self.connection_type == 'server':
            self.label_server_status.setText(f'Статус:\n'
                                             f'Сервер подключён\n'
                                             f'Количество подключённых пользователей: '
                                             f'{len(self.connected_to_server_users)}')
            self.label_server_status.adjustSize()
            self.current_socket.listen(self.max_connections_to_server)

            current_time = strftime('%H:%M:%S', localtime())
            self.plain_text_edit_status_report.insertPlainText(f'{current_time} Server started\n')
        elif self.connection_type == 'client':
            current_time = strftime('%H:%M', localtime())
            self.plain_text_edit_status_report.insertPlainText(f'{current_time} Подключение к серверу\n')

            self.line_edit_user_name.setEnabled(False)
            self.combo_box_recipient_user_name.setEnabled(True)
            self.line_edit_message.setEnabled(True)
            self.button_send.setEnabled(True)

    def create_server(self) -> None:
        self.connection_type = 'server'
        self.view_server_interface()

    def create_client(self) -> None:
        self.connection_type = 'client'
        self.view_client_interface()

    def start_menu(self) -> None:
        if self.current_socket:
            self.current_socket.close()
            self.current_socket = None
        self.view_start_menu_interface()
        self.connection_type = None

    def connection(self) -> None:
        self.address = self.line_edit_address.text()
        self.port = self.line_edit_port.text()

        if self.connection_type == 'server':
            try:
                self.current_socket = socket.create_server((self.address, int(self.port)))
            except OSError:
                self.message_box.setIcon(QMessageBox.Information)
                self.message_box.setText('Адрес или порт уже занят!')
                self.message_box.setStandardButtons(QMessageBox.Ok)
                self.message_box.exec_()
            else:
                self.thread_server_connection = ThreadServerConnection(self.current_socket,
                                                                       self.label_server_status,
                                                                       self.plain_text_edit_status_report,
                                                                       self.connected_to_server_users)
                self.thread_server_connection.start()

                self.connection_mode()
        elif self.connection_type == 'client':
            if not self.line_edit_user_name.text():
                self.message_box.setIcon(QMessageBox.Information)
                self.message_box.setText('Введите имя пользователя!')
                self.message_box.setStandardButtons(QMessageBox.Ok)
                self.message_box.exec_()
            else:
                try:
                    self.current_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.current_socket.connect((self.address, int(self.port)))
                except ConnectionRefusedError:
                    self.message_box.setIcon(QMessageBox.Information)
                    self.message_box.setText('Сервер недоступен!')
                    self.message_box.setStandardButtons(QMessageBox.Ok)
                    self.message_box.exec_()
                else:
                    self.current_socket.send(self.line_edit_user_name.text().encode())
                    self.connection_mode()
                    self.thread_input = ThreadInput(self.current_socket, self.connection_type, None,
                                                    self.combo_box_recipient_user_name, None,
                                                    self.plain_text_edit_status_report, None)
                    self.thread_input.start()
                    self.thread_input.server_disconnect_signal.connect(self.on_client_server_disconnected)

    def on_client_server_disconnected(self) -> None:
        self.message_box.setIcon(QMessageBox.Warning)
        self.message_box.setText('Сервер отключён!')
        self.message_box.setStandardButtons(QMessageBox.Ok)
        self.message_box.exec_()
        self.disconnection()

    def disconnection(self) -> None:
        self.line_edit_address.setEnabled(True)
        self.line_edit_port.setEnabled(True)

        self.button_connection.setEnabled(True)
        self.button_disconnection.setEnabled(False)

        self.combo_box_recipient_user_name.setEnabled(False)

        self.line_edit_message.setEnabled(False)

        if self.connection_type == 'server':
            self.thread_server_connection.stop()
            self.thread_server_connection = None

            self.label_server_status.setText('Статус:\n'
                                             'Сервер отключён')
            self.label_server_status.adjustSize()

            current_time = strftime('%H:%M:%S', localtime())
            self.plain_text_edit_status_report.insertPlainText(f'{current_time} Server disabled\n')
        elif self.connection_type == 'client':
            current_time = strftime('%H:%M', localtime())
            self.plain_text_edit_status_report.insertPlainText(f'{current_time} Отключение от сервера\n')
            self.thread_input.stop()
            self.line_edit_user_name.setEnabled(True)
            self.button_send.setEnabled(False)
            self.line_edit_message.clear()

        if self.current_socket:
            self.current_socket.close()
            self.current_socket = None

    def send(self) -> None:
        if self.combo_box_recipient_user_name.currentText():
            recipient = self.combo_box_recipient_user_name.currentText()
            send_message = self.line_edit_message.text()
            self.current_socket.send(f'{recipient}!&?%{send_message}!&?%'.encode())
            self.line_edit_message.clear()
            current_time = strftime('%H:%M', localtime())
            self.plain_text_edit_status_report.insertPlainText(f'{current_time} '
                                                               f'Отправлено @{recipient}: '
                                                               f'{send_message}\n')


class ThreadServerConnection(QThread):
    def __init__(self, current_socket, label_server_status, plain_text_edit_status_report, connected_to_server_users):
        QThread.__init__(self)
        self.flag = True
        self.server_socket = current_socket
        self.label_server_status = label_server_status
        self.plain_text_edit_status_report = plain_text_edit_status_report
        self.connected_to_server_users = connected_to_server_users
        self.thread_inputs_list = []

    def run(self) -> None:
        self.connection_update()

    def connection_update(self):
        while self.flag:
            try:
                client, address = self.server_socket.accept()
                connected_user_name = client.recv(1024).decode('UTF-8')
                self.connected_to_server_users.append([client, address, connected_user_name])
            except OSError:
                pass
            else:
                current_time = strftime('%H:%M:%S', localtime())
                self.plain_text_edit_status_report.insertPlainText(f'{current_time} Connected {address} '
                                                                   f'as @{connected_user_name}\n')
                thread_input = ThreadInput(self.connected_to_server_users[-1], 'server', self.connected_to_server_users,
                                           None, self.label_server_status, self.plain_text_edit_status_report,
                                           self.server_socket)
                self.thread_inputs_list.append(thread_input)
                thread_input.start()
                self.label_server_status.setText(f'Статус:\n'
                                                 f'Сервер подключён\n'
                                                 f'Количество подключённых пользователей: '
                                                 f'{len(self.connected_to_server_users)}')
                if len(self.connected_to_server_users) > 1:
                    for i in range(len(self.connected_to_server_users)):
                        connected_to_server_users_string = ''
                        for j, client in enumerate(self.connected_to_server_users):
                            if j != i:
                                connected_to_server_users_string += f',{client[2]}'
                        self.connected_to_server_users[i][0].send(f'USERS_LIST'
                                                                  f'{connected_to_server_users_string}'.encode())

    def stop(self):
        for input_thread in self.thread_inputs_list:
            input_thread.stop()
        self.thread_inputs_list = []
        for connection in self.connected_to_server_users:
            connection[0].close()
        self.flag = False


class ThreadInput(QThread):
    server_disconnect_signal = pyqtSignal(str)

    def __init__(self, input_socket, connection_type, connected_to_server_users, combo_box_recipient_user_name,
                 label_server_status, plain_text_edit_status_report, server_socket):
        QThread.__init__(self)
        self.flag = True
        self.socket = input_socket
        self.connection_type = connection_type
        self.connected_to_server_users = connected_to_server_users
        self.combo_box_recipient_user_name = combo_box_recipient_user_name
        self.label_server_status = label_server_status
        self.plain_text_edit_status_report = plain_text_edit_status_report
        self.server_socket = server_socket

    def run(self) -> None:
        self.input_update()

    def input_update(self):
        if self.connection_type == 'server':
            while self.flag:
                try:
                    self.socket[0].send(''.encode())
                    get_message = self.socket[0].recv(1024).decode('UTF-8')
                except Exception:
                    self.connected_to_server_users.remove(self.socket)
                    try:
                        for i in range(len(self.connected_to_server_users)):
                            connected_to_server_users_string = ''
                            for j, client in enumerate(self.connected_to_server_users):
                                if j != i:
                                    connected_to_server_users_string += f',{client[2]}'
                            self.connected_to_server_users[i][0].send(f'USERS_LIST'
                                                                      f'{connected_to_server_users_string}'.encode())
                        current_time = strftime('%H:%M:%S', localtime())
                        if self.flag:
                            self.plain_text_edit_status_report.insertPlainText(f'{current_time} Disconnected '
                                                                               f'{self.socket[1]} '
                                                                               f'as @{self.socket[2]}\n')
                            self.label_server_status.setText(f'Статус:\n'
                                                             f'Сервер подключён\n'
                                                             f'Количество подключённых пользователей: '
                                                             f'{len(self.connected_to_server_users)}')
                            self.label_server_status.adjustSize()
                        self.stop()
                    except Exception:
                        pass
                else:
                    if len(get_message) != 0 and not get_message.startswith('check'):
                        divided_message = get_message.split('!&?%')
                        recipient = divided_message[0]
                        message = divided_message[1]
                        recipient_user = next((user for user in self.connected_to_server_users if user[2] == recipient),
                                              None)
                        recipient_user[0].send(f'MESSAGE!&?%{self.socket[2]}!&?%{message}'.encode())
                        current_time = strftime('%H:%M:%S', localtime())
                        self.plain_text_edit_status_report.insertPlainText(f'{current_time} Send message from '
                                                                           f'@{self.socket[2]} to '
                                                                           f'@{recipient_user[2]}: '
                                                                           f'{message}\n')
                sleep(0.5)

        elif self.connection_type == 'client':
            while self.flag:
                try:
                    self.socket.send(''.encode())
                    get_message = self.socket.recv(1024).decode('UTF-8')
                except ConnectionResetError or ConnectionAbortedError:
                    self.server_disconnect_signal.emit('Сервер отключён!')
                    self.stop()
                except Exception:
                    self.stop()
                else:
                    if not get_message:
                        pass
                    elif get_message.startswith('USERS_LIST'):
                        accepted_users_list = [user for user in get_message.split(',')][1:]
                        self.combo_box_recipient_user_name.clear()
                        for user_name in accepted_users_list:
                            self.combo_box_recipient_user_name.addItem(user_name)
                    elif get_message.startswith('MESSAGE'):
                        divided_message = get_message.split('!&?%')
                        sender = divided_message[1]
                        message = divided_message[2]
                        current_time = strftime('%H:%M', localtime())
                        self.plain_text_edit_status_report.insertPlainText(f'{current_time} '
                                                                           f'Сообщение от @{sender}: '
                                                                           f'{message}\n')
                sleep(0.5)

    def stop(self):
        self.flag = False
        if self.connection_type == 'client':
            self.socket.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TCPConnect()
    main_window.show()
    sys.exit(app.exec_())

# pyinstaller -w -F --onefile --upx-dir=D:\UPX main.py
