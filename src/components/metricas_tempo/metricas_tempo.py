from PyQt6.QtWidgets import QMainWindow,QLabel,QFrame
from src.models.tipos_atividade import TiposAtividade
from src.models.atividade import AtividadeItem
from datetime import datetime,timedelta
from src.components.metricas_tempo.tempos import Tempos
from src.components.metricas_tempo.buttons import MetricasTempoButtons
from src.components.metricas_tempo.modos import Modos

class MetricasTempo:
    def __init__(self,mainWindow:QMainWindow):
        self.modo = Modos.Tudo
        
        self.frame:QFrame = mainWindow.findChild(QFrame,"MetricasDeTempo")
        self.tempoTrabalhoLbl:QLabel = mainWindow.findChild(QLabel,"TempoTrabalhoLbl")
        self.tempoDescansoLbl:QLabel = mainWindow.findChild(QLabel,"TempoDescansoLbl")
        self.tempoTotalLbl:QLabel = mainWindow.findChild(QLabel,"TempoTotalLbl")

        self.buttons = MetricasTempoButtons(mainWindow)
        
        self.buttons.modoChanged.connect(self.setModo)
        self.buttons.VisualizeChanged.connect(self.Hidden)
        self.tempos:Tempos
        self.all_atividades_current:list[AtividadeItem] = list()

    @property
    def atividades_to_view(self):
        match(self.modo):
            case Modos.Tudo:
                return self.all_atividades_current
            case Modos.AFazer:
                output = list(filter(lambda atividade:atividade.completo == False,self.all_atividades_current))
                print(output)
                return output
            case Modos.Feito:
                output = list(filter(lambda atividade:atividade.completo == True,self.all_atividades_current))
                print(output)
                return output
            
    @atividades_to_view.setter
    def atividades_to_view(self,value):
        self.all_atividades_current = value


    def Hidden(self,value:bool):
        if value:
            self.frame.setStyleSheet("color:#172A3A")
            return
        self.frame.setStyleSheet("color:#EFF2F1")

    def setModo(self,modo:str):
        self.modo = modo
        self.setData(self.all_atividades_current)
            

    def setData(self,array_values:list[AtividadeItem]):
        self.tempos = Tempos()
        self.atividades_to_view = array_values
        for atividade in self.atividades_to_view:
            if atividade.tipo_atividade in [TiposAtividade.Estudo,TiposAtividade.Domestica]:
                print("estudo | domestico")
                self.tempos.estudo += atividade.duracao_time_timedelta
            if atividade.tipo_atividade in TiposAtividade.Descanso:
                print('descanso')
                self.tempos.descanso += atividade.duracao_time_timedelta
        self.tempoTrabalhoLbl.setText(f"{self.tempos.estudo:%H:%M:%S}")
        self.tempoDescansoLbl.setText(f"{self.tempos.descanso:%H:%M:%S}")
        self.tempoTotalLbl.setText(f"{self.tempos.total:%H:%M:%S}")
