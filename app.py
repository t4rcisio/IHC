import ctypes
import datetime
import multiprocessing
import os.path
import random
import re
import sys

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QIcon, QIntValidator

from pages import home, buscar, detalhes_fogao, config, login
from pages import elements

class Fogao_Seguro:

    def run(self):
        self.app = QtWidgets.QApplication(sys.argv)

        self.Form = QtWidgets.QWidget()
        self.mPage = home.Ui_Form()
        self.mPage.setupUi(self.Form)


        self.config()

        icon = QIcon(".\\sources\\logo.ico")
        self.Form.setWindowIcon(icon)

        try:
            myappid = "safe_fire" + "001"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except ImportError:
            pass

        self.Form.setWindowTitle("FOGÃO SEGURO - IHC")
        self.Form.show()  # <--- ESSENCIAL

        sys.exit(self.app.exec())

    def config(self):



        self.buscar_widget = QtWidgets.QWidget()
        self.buscar_page = buscar.Ui_Form()
        self.buscar_page.setupUi(self.buscar_widget)

        self.b_layout = QtWidgets.QVBoxLayout(self.buscar_page.widget_3)
        self.b_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.detalhes_widget = QtWidgets.QWidget()
        self.detalhes_page = detalhes_fogao.Ui_Form()
        self.detalhes_page.setupUi(self.detalhes_widget)

        self.d_layout = QtWidgets.QVBoxLayout(self.detalhes_page.widget_3)
        self.d_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.config_widget = QtWidgets.QWidget()
        self.config_page = config.Ui_Form()
        self.config_page.setupUi(self.config_widget)

        validator = QIntValidator(1, 9999)
        self.config_page.time_1.setValidator(validator)
        self.config_page.time_2.setValidator(validator)

        self.login_widget = QtWidgets.QWidget()
        self.login_page = login.Ui_Form()
        self.login_page.setupUi(self.login_widget)

        self.login_page.create.clicked.connect(lambda state: self.create())
        self.login_page.login.clicked.connect(lambda state: self.login())
        self.login_page.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.login_page.password_2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.mPage.stackedWidget.insertWidget(0, self.buscar_widget)
        self.mPage.stackedWidget.insertWidget(1, self.detalhes_widget)
        self.mPage.stackedWidget.insertWidget(2, self.config_widget)
        self.mPage.stackedWidget.insertWidget(3, self.login_widget)


        self.nomes_fogao = {
            "Fogão Brastemp 4 Bocas Fit Pro": {'bocas': 4, "detalhes": {
                1: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
                2: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
                3: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
                4: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
            }},
            "Fogão Brastemp 5 Bocas Inox Deluxe": {'bocas': 5, "detalhes": {
                1: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
                2: {"state": 1, "level": 0.25, "com_panela": True, "start": self.datetime_aleatorio_passado()},
                3: {"state": 1, "level": 0.50, "com_panela": True, "start": self.datetime_aleatorio_passado()},
                4: {"state": 1, "level": 1.00, "com_panela": True, "start": self.datetime_aleatorio_passado()},
                5: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
            }},
            "Fogão Brastemp Elétrico 2 Bocas Premium": {'bocas': 2, "detalhes": {
                1: {"state": 0, "level": 0.00, "com_panela": False, "start": False},
                2: {"state": 1, "level": 1.00, "com_panela": False, "start": self.datetime_aleatorio_passado()}
            }},
        }
        self.lista_nomes = list(self.nomes_fogao.keys())

        self.buscar_page.buscar.clicked.connect(lambda state: self.__buscar())
        self.detalhes_page.voltar.clicked.connect(lambda state: self.mPage.stackedWidget.setCurrentIndex(0))
        self.mPage.config.clicked.connect(lambda state: self.open_config() )
        self.config_page.voltar.clicked.connect(lambda state: self.mPage.stackedWidget.setCurrentIndex(0))

        self.config_page.salvar.clicked.connect(lambda state: self.__save())
        self.config_page.logout.clicked.connect(lambda state: self.log_out())

        self.mPage.stackedWidget.currentChanged.connect(self.__page_change)
        self.current_user = False

        self.show_buscar()
        self.__page_change()

    def __page_change(self):

        self.check_login()

    def log_out(self):

        if not self.confirmar_acao("ATENÇÃO","Tem certeza que deseja sair?"):
            return

        os.remove(".\\temp_login")
        self.mPage.stackedWidget.setCurrentIndex(0)

    def create(self):

        payload = {
            "nome": self.login_page.nome.text(),
            "email": self.login_page.email.text(),
            "password": self.login_page.password.text(),
        }

        if len(payload["nome"].strip()) <=3:
            self.show_error("Erro", f"O campo nome precisa ter pelo menos 3 dígitos")
            return

        if not self.validar_email(payload["email"]):
            self.show_error("Erro", f"O campo email não é válido")
            return

        if len(payload["password"].strip()) <4:
            self.show_error("Erro", f"O campo senha precisa ter pelo menos 4 dígitos")
            return

        try:
            users = eval(open(".\\login", "w", encoding="UTF-8").read())
            if not isinstance(users, dict):
                users = {}
        except:
            users = {}

        if payload["email"] in users:
            self.show_error("Erro", f"Já existe um usuário com esse email")
            return


        users[payload["email"]]  = payload
        open(".\\login", "w", encoding="UTF-8").write(str(users))

        self.show_error("SALVO", f"Usuário criado com sucesso!", QtWidgets.QMessageBox.Icon.Information)

        self.login_page.nome.setText("")
        self.login_page.email.setText("")
        self.login_page.password.setText("")

        self.mPage.stackedWidget.setCurrentIndex(0)

    def confirmar_acao(self, title, message):
        msg = QtWidgets.QMessageBox(self.mPage.widget)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Question)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
                color: #1C1C1E;
            }
            QMessageBox QLabel {
                color: #1C1C1E;
            }
            QMessageBox QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 14px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0A84FF;
            }
        """)

        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No
        )

        msg.button(QtWidgets.QMessageBox.StandardButton.Yes).setText("Sim")
        msg.button(QtWidgets.QMessageBox.StandardButton.No).setText("Não")

        resposta = msg.exec()
        return resposta == QtWidgets.QMessageBox.StandardButton.Yes

    def login(self):

        payload = {
            "email": self.login_page.email_2.text(),
            "password": self.login_page.password_2.text(),
        }

        if not self.validar_email(payload["email"]):
            self.show_error("Erro", f"O campo email não é válido")
            return

        try:
            users = eval(open(".\\login", "r", encoding="UTF-8").read())
            if not isinstance(users, dict):
                users = {}
        except:
            users = {}


        if not payload["email"] in users:
            self.show_error("Erro", f"Email ou senha incorretos")
            return

        if users[payload["email"]]["password"] != payload["password"]:
            self.show_error("Erro", f"Email ou senha incorretos")
            return

        open(".\\temp_login", "w", encoding="UTF-8").write(str(users[payload["email"]]))

        self.mPage.stackedWidget.setCurrentIndex(0)



    def validar_email(self, email: str) -> bool:
        padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(padrao, email) is not None

    def open_config(self):

        self.mPage.stackedWidget.setCurrentIndex(2)

        try:
            data = eval(open("config", "r", encoding="UTF-8").read())

            self.config_page.notifica_gen.setChecked(data['notifica_gen'])
            self.config_page.not_fs.setChecked(data['not_fs'])
            self.config_page.time_1.setText(data["time_1"])
            self.config_page.not_f.setChecked(data['not_f'])
            self.config_page.time_2.setText(data["time_2"])
        except:
            pass





    def __save(self):

        payload = {
            "notifica_gen": self.config_page.notifica_gen.isChecked(),
            "not_fs":self.config_page.not_fs.isChecked(),
            "time_1":self.config_page.time_1.text(),
            "not_f":self.config_page.not_f.isChecked(),
            "time_2":self.config_page.time_2.text(),
        }

        if payload['not_fs']:
            if payload["time_1"] == "":
                self.show_error( "Erro", f"Preencha todos os campos")
                return

        if payload['not_f']:
            if payload["time_2"] == "":
                self.show_error(  "Erro", f"Preencha todos os campos")
                return

        open("config", "w", encoding="UTF-8").write(str(payload))

        self.show_error("SALVO", f"Configurações salvas com sucesso!", QtWidgets.QMessageBox.Icon.Information)
        self.mPage.stackedWidget.setCurrentIndex(0)

    def show_error(self, title, texto, type=QtWidgets.QMessageBox.Icon.Critical):
        msg = QtWidgets.QMessageBox(self.mPage.widget)
        msg.setWindowTitle(title)
        msg.setText(texto)
        msg.setIcon(type)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #1C1C1E;
            }
            QMessageBox QLabel {
                color: #1C1C1E;
            }
            QMessageBox QPushButton {
                background-color: #007AFF;
                color: white;
                border-radius: 6px;
                padding: 5px 14px;
            }
        """)

        msg.exec()

    def check_login(self):

        self.mPage.config.setVisible(False)

        if not os.path.exists(".\\login"):
            self.mPage.stackedWidget.setCurrentIndex(3)
            return

        if not os.path.exists(".\\temp_login"):
            self.mPage.stackedWidget.setCurrentIndex(3)
            return

        try:
            self.current_user = eval(open(".\\temp_login", "r", encoding="UTF-8").read())

            self.config_page.u_name.setText(self.current_user["nome"])
            self.config_page.u_email.setText(self.current_user["email"])
        except:
            self.mPage.stackedWidget.setCurrentIndex(3)
            return

        self.mPage.config.setVisible(True)


    def show_buscar(self):

        self.mPage.stackedWidget.setCurrentIndex(0)

        self.clear_layout(self.b_layout)


        for nome in self.lista_nomes:

            q_row = QtWidgets.QWidget()
            q_row.setStyleSheet("background-color: rgb(229, 229, 234);")
            q_row.setFixedHeight(40)
            q_layout = QtWidgets.QHBoxLayout(q_row)
            q_layout.setContentsMargins(3,3,3,3)

            q_name = QtWidgets.QLineEdit()
            q_name.setFixedHeight(30)
            q_name.setText(nome)
            q_name.setStyleSheet(self.__line_layout())
            q_name.setReadOnly(True)

            q_btn = QtWidgets.QPushButton()
            q_btn.setFixedSize(QtCore.QSize(30,30))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(".\\sources\\next-svgrepo-com.png"), QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
            q_btn.setIcon(icon)
            q_btn.setIconSize(QtCore.QSize(30, 30))
            q_btn.clicked.connect(lambda state, k=nome: self.open_details(k))

            q_layout.addWidget(q_name,5)
            q_layout.addWidget(q_btn, 1)

            self.b_layout.addWidget(q_row)



    def open_details(self, name):

        self.mPage.stackedWidget.setCurrentIndex(1)

        self.detalhes_page.label.setText('<html><head/><body><p align="center"><span style=" font-size:12pt; font-weight:600; color:#2776dd;">'+name+'</span></p></body></html>')

        self.clear_layout(self.d_layout)

        index = 1
        for boca in self.nomes_fogao[name]["detalhes"]:

            q_row = QtWidgets.QWidget()
            q_row.setStyleSheet("background-color: rgb(229, 229, 234);")
            q_row.setFixedHeight(40)
            q_layout = QtWidgets.QHBoxLayout(q_row)
            q_layout.setContentsMargins(3,3,3,3)

            if not self.nomes_fogao[name]["detalhes"][boca]['state']:
                path = ".\\sources\\ice-svgrepo-com.png"
            else:
                path = ".\\sources\\fire-svgrepo-com.png"

            state_btn = QtWidgets.QPushButton()
            state_btn.setFixedSize(QtCore.QSize(30, 30))
            state_icon = QtGui.QIcon()
            state_icon.addPixmap(QtGui.QPixmap(path), QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
            state_btn.setIcon(state_icon)
            state_btn.setIconSize(QtCore.QSize(30, 30))


            q_name = QtWidgets.QLineEdit()
            q_name.setFixedHeight(30)
            q_name.setText(f"BOCA - {index}")
            q_name.setStyleSheet(self.__line_layout())
            q_name.setReadOnly(True)

            q_bar = elements.FlameLevelBar(level=self.nomes_fogao[name]["detalhes"][boca]['level'])

            tempo = self.nomes_fogao[name]["detalhes"][boca]['start']

            if tempo != False:
                tempo = self.calcula_diferenca(tempo)
            else:
                tempo = "N/A"

            q_tempo = QtWidgets.QLineEdit()
            q_tempo.setFixedHeight(30)
            q_tempo.setText(str(tempo))
            q_tempo.setStyleSheet(self.__line_layout())
            q_tempo.setReadOnly(True)

            q_btn = QtWidgets.QPushButton()
            q_btn.setFixedSize(QtCore.QSize(30,30))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(".\\sources\\next-svgrepo-com.png"), QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
            q_btn.setIcon(icon)
            q_btn.setIconSize(QtCore.QSize(30, 30))
            q_btn.clicked.connect(lambda state, k=name, j=index: self.open_details_boca(k, j))

            q_layout.addWidget(state_btn, 1)
            q_layout.addWidget(q_name,5)
            q_layout.addWidget(q_bar, 3)
            q_layout.addWidget(q_tempo, 2)
            #q_layout.addWidget(q_btn, 1)

            self.d_layout.addWidget(q_row)
            index +=1


    def open_details_boca(self, nome, boca):

        pass

    def __buscar(self):

        self.lista_nomes = list(self.nomes_fogao.keys())
        random.shuffle(self.lista_nomes )
        self.show_buscar()

    def calcula_diferenca(self, tempo):

        agora = datetime.datetime.now()
        diff = agora - tempo
        return str(int(diff.total_seconds() / 60)) + " min."

    def datetime_aleatorio_passado(self):
        # sorteia entre 5 e 30 minutos
        minutos = random.randint(5, 30)

        # subtrai do agora
        return datetime.datetime.now() - datetime.timedelta(minutes=minutos)

    def clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                if item.layout() is not None:
                    self.clear_layout(item.layout())

    def __line_layout(self):

        return """
        QLineEdit {
    background-color: #FFFFFF;        /* fundo branco iOS */
    color: #1C1C1E;                   /* texto preto iOS */
    border: 1.5px solid #D1D1D6;      /* cinza leve iOS */
    border-radius: 10px;              /* canto arredondado iOS */
    font-size: 12px;
}

QLineEdit:focus {
    border: 1.5px solid #007AFF;      /* azul iOS quando focado */
    outline: none;
}

        
        """






if __name__ == "__main__":
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

    AO = Fogao_Seguro()
    AO.run()