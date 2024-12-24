from datetime import datetime
from PyQt6.QtWidgets import QListWidget,QMainWindow,QPushButton
from PyQt6.QtGui import QBrush,QColor,QIcon
from PyQt6.QtCore import Qt,QPoint,pyqtSignal,QObject
from src.components.metricas_tempo.modos import Modos
from src.models.periodos import Periodo
from src.models.atividade import AtividadeItem
from src.db import Db
from src.resources.icons import Icons

class MetricasTempoButtons(QListWidget):
    modoChanged = pyqtSignal(str)
    VisualizeChanged = pyqtSignal(bool)
    def __init__(self,mainWindow:QMainWindow):
        super().__init__()
        self.icons = Icons()
        self.modoBtn:QPushButton = mainWindow.findChild(QPushButton,"ModoBtn")
        self.visualizarBtn:QPushButton = mainWindow.findChild(QPushButton,"VisualizarBtn")
        
        self.modoBtn.clicked.connect(lambda:self.nextModo())

        self.__modo = Modos.Tudo
        self.__modo_step = Modos.Modos.copy()
        self.nextModo()

        self.__visualize = False
        self.visualizarBtn.clicked.connect(lambda:self.nextVisualize())
        self.nextVisualize()
    
    def nextModo(self):
        if self.__modo_step.__len__() == 0:
            self.__modo_step = Modos.Modos.copy()

        self.__modo = self.__modo_step.pop(-1)
        match(self.__modo):
            case Modos.Tudo:
                self.modoBtn.setIcon(self.icons.circleDark)
            case Modos.AFazer:
                self.modoBtn.setIcon(self.icons.taskUndone)
            case Modos.Feito:
                self.modoBtn.setIcon(self.icons.taskDone)
        self.modoChanged.emit(self.__modo)

    def nextVisualize(self):
        if self.__visualize == True:
            self.__visualize = False
            self.visualizarBtn.setIcon(self.icons.ClosedEye)
        else:
            self.__visualize = True
            self.visualizarBtn.setIcon(self.icons.OpenedEye)
        self.VisualizeChanged.emit(self.__visualize)
        