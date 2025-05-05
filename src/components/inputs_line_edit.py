from datetime import datetime
from PyQt6.QtWidgets import QMainWindow,QLineEdit,QComboBox,QDateEdit
from PyQt6.QtCore import QDate,pyqtSignal,QObject
from ..models import AtividadeItem
from ..models.atividade import pattern_HMS,pattern_MS
from re import compile as cmp,DOTALL
from logging import debug

pattern_atividade_ferretto = cmp(r"(\d\d:\d\d)\sRelevância Enem\s\w+\s([^\n]+)",DOTALL)
pattern_atividade_manual = cmp(r"(\d\d:\d\d) (\w+) ([^\n]+)")

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

    def __get_values_matches(self,tuple_values:tuple) -> AtividadeItem | None:
        item = AtividadeItem()
        if tuple_values.__len__() == 3:
            item.duracao = tuple_values[0]
            item.materia = tuple_values[1]
            item.nome = item.materia + " " +tuple_values[2]
            return item
        return
    

    def __get_duracao_e_nome_from_atividadeNomeLineEdit(self)->AtividadeItem|list[AtividadeItem] | None:
        output:list[AtividadeItem] = list()

        atividades_str = self.nomeAtividadeLineEdit.text()
        
        atividade_ferretto_match = pattern_atividade_ferretto.findall(atividades_str)
        atividade_manual_match = pattern_atividade_manual.findall(atividades_str)

        match_to_make_items:list
        if atividade_ferretto_match:
            match_to_make_items = atividade_ferretto_match
        elif atividade_manual_match:
            match_to_make_items = atividade_manual_match
        else: # nenhum valor encontrado
            debug("Nenhum valor encontrado em AtividadeNomeLineEdit")
            return 
        
        for tuple_values in match_to_make_items:
            item = self.__get_values_matches(tuple_values)
            if item is not None:
                output.append(item)
        match(output.__len__()):
            case 0:
                return
            case 1:
                return output[0]
            case _:
                return output
    
    def emitTimeVarChanged(self):
        self.TimeVarChanged.emit(self.PeriodoCbx.currentText())


    @property
    def data_in_dateEdit(self)->datetime:
        return self.dateEdit.date().toPyDate()
    
    
    @property
    def cadastro(self) -> AtividadeItem | list[AtividadeItem] |None:
        items = self.__get_duracao_e_nome_from_atividadeNomeLineEdit()
        date_time_edit = self.data_in_dateEdit
        periodo = self.PeriodoCbx.currentText()
        if isinstance(items,list):
            for item in items:
                item.data = date_time_edit
                item.periodo = periodo
        if isinstance(items,AtividadeItem):
            items.data = date_time_edit
            items.periodo = periodo
        return items
        
    
    @cadastro.setter
    def cadastro(self,value:AtividadeItem):
        if value == None:
            self.nomeAtividadeLineEdit.setText("")
            return
        self.nomeAtividadeLineEdit.setText(value.duracao_str+ " "+value.nome)
        self.__cadastro_atual = value