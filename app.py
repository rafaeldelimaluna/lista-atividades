from  datetime import datetime
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication,QPushButton,QStatusBar
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
from src.models.atividade import AtividadeItem
from src.models.tipos_atividade import TiposAtividade
from src.components import *
from src.db import Db
from src.components.editar_item import EditarItem
from src.resources import Icons
from logging import DEBUG, basicConfig,WARNING

basicConfig(level=WARNING,format="\033[;30m%(levelname)s\033[;32m:%(filename)s \033[m| %(funcName)s:%(lineno)d ->\033[;33m%(message)s\033[m")

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/gui.ui",self)
        self.setWindowIcon(Icons().appIcon)
        self.setWindowIconText("Lista de Atividades")
        self.setWindowTitle("Lista de Atividades")


        self.db = Db()

        self.inputs = InputsLineEdit(self)
        self.lista_atividades = ListaAtividades(self,self.db)
        self.metricas_tempo = MetricasTempo(self)
        self.lista_atividades.ListUpdated.connect(self.metricas_tempo.setData)
        self.status_bar:QStatusBar = self.findChild(QStatusBar,"statusbar")

        self.inputs.TimeVarChanged.connect(self.lista_atividades.setPeriodo)
        self.inputs.TimeVarChanged.connect(lambda:self.lista_atividades.setData(self.inputs.data_in_dateEdit))
        self.inputs.emitTimeVarChanged()
        
        self.tempo_trabalho_secao = datetime.today().min

        
    def keyPressEvent(self, event:QKeyEvent):
        cadastro_atual = self.inputs.cadastro
        print(cadastro_atual)
        if event.key() in [Qt.Key.Key_Return,Qt.Key.Key_Enter] and cadastro_atual is not None and isinstance(cadastro_atual,AtividadeItem):
            items = self.inputs.cadastro
            self.db.add(items)
            if items.tipo_atividade == TiposAtividade.Descanso:
                self.tempo_trabalho_secao = datetime.today().min
            else:
                self.tempo_trabalho_secao+= items.duracao_time_timedelta
            self.status_bar.showMessage(f"Tempo Trabalho: {self.tempo_trabalho_secao:%H:%M:%S}")
            self.lista_atividades.update_list()
            self.inputs.cadastro = None
            self.inputs.emitTimeVarChanged()

        if event.key() in [Qt.Key.Key_Return,Qt.Key.Key_Enter] and cadastro_atual is not None and isinstance(cadastro_atual,list):
            items = self.inputs.cadastro
            self.db.add(items)
            for item in items:
                if item.tipo_atividade == TiposAtividade.Descanso:
                    self.tempo_trabalho_secao = datetime.today().min
                else:
                    self.tempo_trabalho_secao+= item.duracao_time_timedelta
            self.status_bar.showMessage(f"Tempo Trabalho: {self.tempo_trabalho_secao:%H:%M:%S}")
            self.lista_atividades.update_list()
            self.inputs.cadastro = None
            self.inputs.emitTimeVarChanged()


        if event.key() == Qt.Key.Key_Escape:
            self.close()


        if event.key() == Qt.Key.Key_Delete and self.lista_atividades.widget.hasFocus():
            self.lista_atividades.delete_current_item()

if __name__ == "__main__":
    app = QApplication([])
    ui = Main()
    ui.show()
    app.exec()