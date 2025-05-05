from datetime import datetime
from src.db import Db
from src.models import Periodo,AtividadeItem
from src.models.tipos_atividade import TiposAtividade
from src.google_module import MyGoogleEngine

context = Db()

class AtividadePeriodoItem:
    def __init__(self,lista_atividades:list[AtividadeItem]):
        self.lista_atividades = list(filter(lambda atividade_item: atividade_item.data,lista_atividades))
        #self.lista_atividades = list(filter(lambda atividade_item: atividade_item.data==datetime(2030,1,1).date(),lista_atividades))
        
    @property
    def estudo(self)->list[AtividadeItem]:
        return list(filter(lambda atividade_item:atividade_item.tipo_atividade == TiposAtividade.Estudo and atividade_item.completo == True,self.lista_atividades))
    
    @property
    def descanso(self) ->list[AtividadeItem]:
        return list(filter(lambda atividade_item:atividade_item.tipo_atividade == TiposAtividade.Descanso and atividade_item.completo == True,self.lista_atividades))
    
    def __calc_duracao(self,lista_atividades:list[AtividadeItem]):
        duracao = datetime.now().min
        for item in lista_atividades:
            duracao+=item.duracao_time_timedelta
        return duracao

    @property
    def tempo_estudo(self) ->datetime:
        return self.__calc_duracao(self.estudo)

class AtividadesPeriodo:
    def __init__(self):
        self.manha = AtividadePeriodoItem(context.get_all(Periodo.Manha))
        self.tarde = AtividadePeriodoItem(context.get_all(Periodo.Tarde))
        self.noite = AtividadePeriodoItem(context.get_all(Periodo.Noite))
        self.todos = AtividadePeriodoItem(context.get_all())



# atividades = AtividadesPeriodo()
# db = Db()
MyGoogleEngine().sync_database()

