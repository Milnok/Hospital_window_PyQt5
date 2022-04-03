import requests
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton

from login_window import Ui_Login_window
from main_window import Ui_MainWindow
from create_window import Ui_Create_note
from edit_window import Ui_Edit_window


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.token = None
        self.first_name = None
        self.last_name = None
        self.type = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.create_app = CreateWindow()
        self.edit_app = EditWindow()

        self.ui.main_btn_create.clicked.connect(self.create_note)
        self.ui.main_btn_quit.clicked.connect(self.quit)

    def get_notes(self):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        res = requests.get('http://127.0.0.1:8000/api/v1/get_notes', headers=headers)
        table = self.ui.main_table_note
        for i in range(table.rowCount()):
            table.removeRow(0)
        edit_button_dict = {}
        delete_button_dict = {}
        for row in res.json():
            edit_button_dict[row.get('id')] = QtWidgets.QPushButton('Редактировать')
            delete_button_dict[row.get('id')] = QtWidgets.QPushButton('Удалить')
            row_count = table.rowCount()
            table.insertRow(row_count)
            table.setItem(row_count, 0, QTableWidgetItem(
                row.get('doctor').get('first_name') + ' ' + row.get('doctor').get('last_name')))
            table.setItem(row_count, 1, QTableWidgetItem(
                row.get('patient').get('first_name') + ' ' + row.get('patient').get('last_name')))
            table.setItem(row_count, 2, QTableWidgetItem(row.get('description')))
            if self.type == 'Doctor':
                table.setCellWidget(row_count, 3, edit_button_dict[row.get('id')])
                table.setCellWidget(row_count, 4, delete_button_dict[row.get('id')])
                edit_button_dict.get(row.get('id')).clicked.connect(
                    lambda checked, i=row.get('id'): self.edit_note(i))
                delete_button_dict.get(row.get('id')).clicked.connect(
                    lambda checked, i=row.get('id'): self.delete_note(i))

    def get_timetable(self):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        res = requests.get('http://127.0.0.1:8000/api/v1/get_timetable', headers=headers)
        table = self.ui.main_table_time
        for i in range(table.rowCount()):
            table.removeRow(0)
        for row in res.json():
            rowCount = table.rowCount()
            table.insertRow(rowCount)
            table.setItem(rowCount, 0, QTableWidgetItem(
                row.get('doctor').get('first_name') + ' ' + row.get('doctor').get('last_name')))
            table.setItem(rowCount, 1, QTableWidgetItem(
                row.get('monday_start') + ' - ' + row.get('monday_end')))
            table.setItem(rowCount, 2, QTableWidgetItem(
                row.get('tuesday_start') + ' - ' + row.get('tuesday_end')))
            table.setItem(rowCount, 3, QTableWidgetItem(
                row.get('wednesday_start') + ' - ' + row.get('wednesday_end')))
            table.setItem(rowCount, 4, QTableWidgetItem(
                row.get('thursday_start') + ' - ' + row.get('thursday_end')))
            table.setItem(rowCount, 5, QTableWidgetItem(
                row.get('friday_start') + ' - ' + row.get('friday_end')))

    def edit_note(self, id):
        data = {
            'id': id,
            'token': self.token
        }
        self.edit_app.show_data(data)

    def delete_note(self, id):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        res = requests.delete('http://127.0.0.1:8000/api/v1/delete_note/' + str(id), headers=headers)
        if res.status_code == 204:
            main_app.get_notes()

    def show_data(self, data):
        super(MainWindow, self).show()
        self.token = data.get('token')
        self.check_login()
        if self.type == 'Patient':
            self.ui.main_btn_create.hide()
        self.get_notes()
        self.get_timetable()

    def create_note(self):
        data = {
            'token': self.token,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
        self.create_app.show_data(data)

    def check_login(self):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        res = requests.get('http://127.0.0.1:8000/api/v1/check_login', headers=headers).json()
        self.ui.main_lable_name.setText(res.get('login_first') + ' ' + res.get('login_last'))
        self.first_name = res.get('login_first')
        self.last_name = res.get('login_last')
        self.type = res.get('type')

    def quit(self):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        requests.get('http://127.0.0.1:8000/auth/token/logout/', headers=headers).json()
        login_app.show()
        main_app.hide()


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_Login_window()
        self.ui.setupUi(self)
        self.ui.login_btn.clicked.connect(self.login)

    def login(self):
        data = {
            'username': self.ui.login_username.text(),
            'password': self.ui.login_password.text()
        }
        res = requests.post('http://127.0.0.1:8000/auth/token/login/', data=data)
        if res.json().get('auth_token') is not None:
            main_app.show_data({'token': res.json().get('auth_token')})
            self.ui.login_password.clear()
            self.close()


class CreateWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(CreateWindow, self).__init__()
        self.token = None
        self.ui = Ui_Create_note()
        self.ui.setupUi(self)
        self.ui.create_btn.clicked.connect(self.create_note)

    def create_note(self):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        data = {
            'doctor.first_name': self.ui.create_doctor_first.text(),
            'doctor.last_name': self.ui.create_doctor_last.text(),
            'patient.first_name': self.ui.create_pacient_first.text(),
            'patient.last_name': self.ui.create_pacient_last.text(),
            'description': self.ui.create_text.toPlainText(),
        }
        res = requests.post('http://127.0.0.1:8000/api/v1/create_note', headers=headers, data=data)
        if res.status_code == 204:
            main_app.get_notes()
            self.ui.create_doctor_first.clear()
            self.ui.create_doctor_last.clear()
            self.ui.create_pacient_first.clear()
            self.ui.create_pacient_last.clear()
            self.ui.create_text.clear()
            self.close()

    def show_data(self, data):
        super(CreateWindow, self).show()
        self.token = data.get('token')
        self.ui.create_doctor_first.setText(data.get('first_name'))
        self.ui.create_doctor_last.setText(data.get('last_name'))


class EditWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(EditWindow, self).__init__()
        self.note_id = None
        self.token = None
        self.ui = Ui_Edit_window()
        self.ui.setupUi(self)

        self.ui.edit_btn.clicked.connect(self.edit)

    def show_data(self, data):
        super(EditWindow, self).show()
        self.token = data.get('token')
        self.note_id = data.get('id')
        headers = {
            'Authorization': 'Token ' + self.token
        }
        data = {
            'id': str(self.note_id),
        }
        res = requests.get('http://127.0.0.1:8000/api/v1/get_note_by_id', headers=headers, params=data)
        if res.status_code == 200:
            note = res.json()[0]
            self.ui.edit_doctor.setText(
                note.get('doctor').get('first_name') + ' ' + note.get('doctor').get('last_name'))
            self.ui.edit_pacient.setText(
                note.get('patient').get('first_name') + ' ' + note.get('patient').get('last_name'))
            self.ui.edit_text.setText(note.get('description'))

    def edit(self):
        headers = {
            'Authorization': 'Token ' + self.token
        }
        data = {
            'description': self.ui.edit_text.toPlainText(),
        }
        res = requests.patch('http://127.0.0.1:8000/api/v1/update_note/' + str(self.note_id), headers=headers,
                             data=data)
        if res.status_code == 200:
            main_app.get_notes()
            self.ui.edit_pacient.clear()
            self.ui.edit_doctor.clear()
            self.ui.edit_text.clear()
            self.close()


app = QtWidgets.QApplication([])

main_app = MainWindow()
main_app.hide()
login_app = LoginWindow()
login_app.show()

sys.exit(app.exec())
