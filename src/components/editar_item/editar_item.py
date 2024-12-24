from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication,QPushButton,QDateEdit,QComboBox,QLineEdit,QStatusBar,QWidget
from PyQt6.QtCore import Qt,QDate
from src.models.atividade import AtividadeItem
from src.components import *
from src.db import Db

class EditarItem(QMainWindow):
    def __init__(self,atividade_item:AtividadeItem):
        super().__init__()
        uic.loadUi("src/ui/editar_item.ui")
        
        self.db = Db()
        self.atividade_item = atividade_item

        self.DuracaoLineEdit:QLineEdit = self.findChild(QLineEdit,"DuracaoLineEdit")
        self.NomeAtividadeLineEdit:QLineEdit = self.findChild(QLineEdit,"NomeAtividadeLineEdit")
        self.dateEdit:QDateEdit = self.findChild(QDateEdit,"dateEdit")
        self.periodoCbx:QComboBox = self.findChild(QComboBox,"PeriodoCbx")
        self.statusBar:QStatusBar = self.findChild(QStatusBar,"statusbar")
        self.editBtn:QPushButton = self.findChild(QPushButton,"EditBtn")
        self.show()

    @property
    def cadastro(self)->AtividadeItem|None:
        item = AtividadeItem()
        item.duracao =self.DuracaoLineEdit.text()
        item.nome = self.NomeAtividadeLineEdit.text()
        item.data= self.dateEdit.date().toPyDate()
        item.periodo = self.periodoCbx.currentText()
        if item.duracao == None:
            return None
        return item
    
    def setDate(self):
        self.DuracaoLineEdit.setText(self.atividade_item.duracao_str)
        self.NomeAtividadeLineEdit.setText(self.atividade_item.nome)
        self.dateEdit.setDate(QDate().setDate(year=self.atividade_item.data.year,month=self.atividade_item.data.month,day=self.atividade_item.data.day))
        self.periodoCbx.setCurrentText(self.atividade_item.periodo)

    def edit(self):
        if isinstance(self.cadastro,AtividadeItem):
            self.db.update(self.atividade_item)
            self.close()
        else:
            self.statusBar.showMessage("Há algum erro nas entradas dos formulários")
