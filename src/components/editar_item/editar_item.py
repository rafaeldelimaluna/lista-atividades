from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication,QPushButton,QDateEdit,QComboBox,QLineEdit,QStatusBar,QWidget
from PyQt6.QtCore import Qt,QDate
from src.models.atividade import AtividadeItem
from src.components import *
from src.db import Db

class EditarItem(QMainWindow):
    def __init__(self,atividade_item:AtividadeItem):
        super().__init__()
        uic.loadUi("./src/ui/editar_item.ui",self)
        
        self.db = Db()
        self.atividade_item = atividade_item

        self.DuracaoLineEdit:QLineEdit = self.findChild(QLineEdit,"DuracaoLineEdit")
        self.NomeAtividadeLineEdit:QLineEdit = self.findChild(QLineEdit,"NomeAtividadeLineEdit")
        self.dateEdit:QDateEdit = self.findChild(QDateEdit,"dateEdit")
        self.periodoCbx:QComboBox = self.findChild(QComboBox,"PeriodoCbx")
        self.statusBar:QStatusBar = self.findChild(QStatusBar,"statusbar")
        self.editBtn:QPushButton = self.findChild(QPushButton,"EditBtn")

        self.editBtn.clicked.connect(lambda:self.edit())

        self.__set_values()

        self.show()


    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()
        if a0.key() in [Qt.Key.Key_Enter,Qt.Key.Key_Return]:
            self.edit()
            
    @property
    def cadastro(self)->AtividadeItem|None:
        item = AtividadeItem()
        item.id = self.atividade_item.id
        item.duracao =self.DuracaoLineEdit.text()
        item.nome = self.NomeAtividadeLineEdit.text()
        item.data= self.dateEdit.date().toPyDate()
        item.periodo = self.periodoCbx.currentText()
        item.completo = self.atividade_item.completo
        if item.duracao == None:
            return None
        return item
    
    def setDate(self):
        self.DuracaoLineEdit.setText(self.atividade_item.duracao_str)
        self.NomeAtividadeLineEdit.setText(self.atividade_item.nome)
        self.dateEdit.setDate(QDate().setDate(year=self.atividade_item.data.year,month=self.atividade_item.data.month,day=self.atividade_item.data.day))
        self.periodoCbx.setCurrentText(self.atividade_item.periodo)

    def edit(self):
        """Sem erro: True \n Com erro: False"""
        if isinstance(self.cadastro,AtividadeItem):
            self.db.update(self.cadastro)
            self.close()
            return
        self.statusBar.showMessage("Há algum erro nas entradas dos formulários")


    def __set_values(self):
        if not self.atividade_item:
            return
        self.NomeAtividadeLineEdit.setText(self.atividade_item.nome)
        self.DuracaoLineEdit.setText(self.atividade_item.duracao_str)
        self.periodoCbx.setCurrentText(self.atividade_item.periodo)
        self.dateEdit.setDate(self.atividade_item.data)