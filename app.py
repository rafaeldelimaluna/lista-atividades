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
from logging import DEBUG,INFO, basicConfig,WARNING,info
from src.google_module import MyGoogleEngine

basicConfig(level=INFO,format="\033[;30m%(levelname)s\033[;32m:%(filename)s \033[m| %(funcName)s:%(lineno)d ->\033[;33m%(message)s\033[m")

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/gui.ui",self)
        self.setWindowIcon(Icons().appIcon)
        self.setWindowIconText("Lista de Atividades")
        self.setWindowTitle("Lista de Atividades")


        self.db = Db()
        info("Loading MyGoogleEngine")
        self.google_engine = MyGoogleEngine(self.db)
        self.google_engine.sync_database()
        info("MyGoogleEngine loaded")

        self.inputs = InputsLineEdit(self)
        self.lista_atividades = ListaAtividades(self,self.db)
        self.metricas_tempo = MetricasTempo(self)
        self.lista_atividades.ListUpdated.connect(self.metricas_tempo.setData)
        self.status_bar:QStatusBar = self.findChild(QStatusBar,"statusbar")

        self.inputs.TimeVarChanged.connect(self.lista_atividades.setPeriodo)
        self.inputs.TimeVarChanged.connect(lambda:self.lista_atividades.setData(self.inputs.data_in_dateEdit))
        self.inputs.emitTimeVarChanged()
        
        self.tempo_trabalho_secao = datetime.today().min

    def tentar_cadastrar(self,cadastro_atual:AtividadeItem|list[AtividadeItem]|None):
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

    def keyPressEvent(self, event:QKeyEvent):
        cadastro_atual = self.inputs.cadastro
        print("Cadastro Atual:",cadastro_atual)
        if event.key() in [Qt.Key.Key_Return,Qt.Key.Key_Enter] and cadastro_atual is not None and isinstance(cadastro_atual,AtividadeItem):
            self.tentar_cadastrar(cadastro_atual)

        if event.key() in [Qt.Key.Key_Return,Qt.Key.Key_Enter] and cadastro_atual is not None and isinstance(cadastro_atual,list):
            items = self.inputs.cadastro
            for item in items:
                self.tentar_cadastrar(item)

        if event.key() == Qt.Key.Key_Escape:
            self.close()


        if event.key() == Qt.Key.Key_Delete and self.lista_atividades.widget.hasFocus():
            self.lista_atividades.delete_current_item()

    def push_atividades_white_google_id_to_google_tasks(self):
        atividade_items = self.db.get_all_white_google_id()
        for item in atividade_items:
            task = self.google_engine.add(item)
            item.google_id = task["id"]
            item.google_etag = task["etag"]
            self.db.update(item,False)

    def sync_google_tasks(self):
        """Nesta função, o banco de dados passa os dados para a API"""
        self.push_atividades_white_google_id_to_google_tasks()
        atividades_com_novas_etags:list[AtividadeItem] = []
        print(self.db.objeto_das_atividades_modificadas)
        for atividade_modificada in self.db.objeto_das_atividades_modificadas:
            print("------------------------")
            print("atividade velha:",atividade_modificada.__dict__)
            atividade_modificada.google_etag = self.google_engine.update(atividade_modificada)["etag"]
            print("atividade nova:",atividade_modificada.__dict__)
            atividades_com_novas_etags.append(atividade_modificada)
            
        self.db.objeto_das_atividades_modificadas.clear()
        self.db.update_many_etags(atividades_com_novas_etags)


        for google_id_atividade_removida in self.db.google_id_das_atividades_removidas:
            self.google_engine.remove(google_id_atividade_removida)

        self.db.google_id_das_atividades_removidas.clear()

    def closeEvent(self,event):
        self.sync_google_tasks()
        self.google_engine.sync_database()
        self.db.update_last_entry()

if __name__ == "__main__":
    app = QApplication([])
    ui = Main()
    ui.show()
    app.exec()
