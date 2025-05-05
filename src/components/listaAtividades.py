from datetime import datetime
from PyQt6.QtWidgets import QListWidget,QMainWindow,QListWidgetItem,QMenu
from PyQt6.QtGui import QBrush,QColor
from PyQt6.QtCore import Qt,QPoint,pyqtSignal,QObject
from src.models.tipos_atividade import TiposAtividade
from src.models.periodos import Periodo
from src.models.atividade import AtividadeItem
from src.db import Db
from src.resources import Icons
from src.components.editar_item import EditarItem

class ListaAtividades(QListWidget):
    ListUpdated = pyqtSignal(list)

    def __init__(self,mainWindow:QMainWindow,db:Db):
        super().__init__()
        self.icons = Icons()
        self.__periodo = Periodo.Todos
        self.__data = None
        self.editar_item:EditarItem
        self.widget:QListWidget = mainWindow.findChild(QListWidget,"ListaListWidget")
        self.db = db

        self.widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.widget.customContextMenuRequested.connect(self.__show_context_menu)


        self.widget.itemDoubleClicked.connect(lambda atividade_item:self.__toggle_current_item_complete(atividade_item.data(Qt.ItemDataRole.UserRole)))
        self.__start()

    @property
    def lista_atividades_in_list_widget(self)->list[AtividadeItem]:
        atividades:list[AtividadeItem] = list()
        for row_index in range(self.widget.count()):
            item:AtividadeItem = self.widget.item(row_index).data(Qt.ItemDataRole.UserRole)
            atividades.append(item)
        return atividades


    @property
    def currentAtividade(self):
        if self.widget.currentItem() == None:
            return
        current_widget_item = self.widget.currentItem()
        current_item = current_widget_item.data(Qt.ItemDataRole.UserRole)
        return current_item
    
    
    def setData(self,value:datetime):
        self.__data = value
        self.update_list()


    @property
    def periodo(self):
        return self.__periodo
    

    @periodo.setter
    def periodo(self,value:str):
        self.__periodo = value
        self.update_list()
        print(value)
        
    def setPeriodo(self,value:str):
        self.periodo = value


    def __toggle_current_item_complete(self,atividade_item:AtividadeItem):
        print(atividade_item.__dict__)
        if atividade_item.completo == True:
            atividade_item.completo = False
        else:
            atividade_item.completo = True
        self.db.update(atividade_item,True)
        self.update_list()

    def update_list(self):
        self.widget.clear()
        lista_atividades = self.db.get_all(self.periodo,self.__data)
        for atividade in lista_atividades:
            item = QListWidgetItem(atividade.nome + " | "+atividade.duracao_str)
            item.setData(Qt.ItemDataRole.UserRole,atividade)
            if atividade.completo:
                item.setBackground(QBrush(QColor("#63cf80")))
            match(atividade.tipo_atividade):
                case TiposAtividade.Descanso:
                    item.setIcon(self.icons.SleepWhite)
                case TiposAtividade.Domestica:
                    item.setIcon(self.icons.House)
                case TiposAtividade.Estudo:
                    item.setIcon(self.icons.Hammer)
            self.widget.addItem(item)
        self.ListUpdated.emit(lista_atividades)

    def delete_current_item(self):
        current_item = self.currentAtividade
        if current_item == None:
            return
        self.db.deleteByItem(current_item)
        self.widget.takeItem(self.widget.currentRow())
        self.ListUpdated.emit(self.lista_atividades_in_list_widget)

    def __show_context_menu(self,position:QPoint):
        menu = QMenu(self.widget)
        action_editar_item = menu.addAction("Editar Atividade")

        action = menu.exec(self.widget.mapToGlobal(position))
        print('show context menu')
        if action == action_editar_item:
            print('editando')
            self.editar_item = EditarItem(self.currentAtividade)
            self.editar_item.show()

    def __start(self):
        self.update_list()
