from datetime import datetime
from PyQt6.QtWidgets import QMainWindow,QLineEdit,QComboBox,QDateEdit
from PyQt6.QtCore import QDate,pyqtSignal,QObject
from ..models import AtividadeItem
from ..models.atividade import pattern_HMS,pattern_MS
from re import compile as cmp,DOTALL

pattern_atividade_ferretto = cmp(r"(\d\d:\d\d)\sRelevância Enem\s\w+\s([^\n]+)",DOTALL)
pattern_atividade_manual = cmp(r"(\d\d:\d\d) ([^\n]+)")

class InputsLineEdit(QObject):
    TimeVarChanged = pyqtSignal(str)
    def __init__(self, mainWindow:QMainWindow):
        super().__init__()
        self.nomeAtividadeLineEdit:QLineEdit = mainWindow.findChild(QLineEdit,"NomeAtividadeLineEdit")
        self.PeriodoCbx:QComboBox = mainWindow.findChild(QComboBox,"PeriodoCbx")
        self.dateEdit:QDateEdit = mainWindow.findChild(QDateEdit,"dateEdit")
        self.dateEdit.setDate(QDate.currentDate())
        
        self.dateEdit.dateChanged.connect(self.emitTimeVarChanged)
        self.PeriodoCbx.currentTextChanged.connect(self.emitTimeVarChanged)
        self.__cadastro_atual = AtividadeItem()

    def __get_duracao_e_nome_from_atividadeNomeLineEdit(self)->AtividadeItem:
        item = AtividadeItem()
        atividade = self.nomeAtividadeLineEdit.text()
        
        atividade_ferretto_match = pattern_atividade_ferretto.findall(atividade)
        atividade_manual_match = pattern_atividade_manual.findall(atividade)

        if atividade_ferretto_match:
            item.duracao = atividade_ferretto_match[0][0]
            item.nome = atividade_ferretto_match[0][1]
            return item
        elif atividade_manual_match:
            item.duracao = atividade_manual_match[0][0]
            item.nome = atividade_manual_match[0][1]
            return item
        else:
            return item
    
    def emitTimeVarChanged(self):
        self.TimeVarChanged.emit(self.PeriodoCbx.currentText())


    @property
    def data_in_dateEdit(self)->datetime:
        return self.dateEdit.date().toPyDate()
    
    
    @property
    def cadastro(self) -> AtividadeItem | None:
        item = AtividadeItem()
        nome_e_duracao = self.__get_duracao_e_nome_from_atividadeNomeLineEdit()
        if nome_e_duracao.nome == None or nome_e_duracao.duracao == None:
            return
        item.duracao = nome_e_duracao.duracao_str
        item.nome = nome_e_duracao.nome

        item.data = self.data_in_dateEdit
        item.periodo = self.PeriodoCbx.currentText()
        return item
        
    
    @cadastro.setter
    def cadastro(self,value:AtividadeItem):
        if value == None:
            self.nomeAtividadeLineEdit.setText("")
            return
        self.nomeAtividadeLineEdit.setText(value.duracao_str+ " "+value.nome)
        self.__cadastro_atual = value