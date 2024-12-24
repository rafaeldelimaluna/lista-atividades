from dataclasses import dataclass
from datetime import datetime,date, timedelta
import datetime as dt
from re import compile as cmp
from src.models.tipos_atividade import TiposAtividade
from src.models.periodos import Periodo
from unidecode import unidecode
pattern_HMS = cmp(r"(\d\d):(\d\d):(\d\d)")
pattern_MS = cmp(r"(\d\d):(\d\d)")


class AtividadeItem:
    def __init__(self):
        self.id:int = 0
        self.__nome:str = None
        self.__duracao:datetime = None
        self.completo:bool = False
        self.periodo:str
        self.__data:date = None
        self.tipo_atividade = None

    def set_values_by_array(self,values_array):
        self.id = values_array[0]
        self.nome = values_array[1]
        self.duracao = values_array[2]
        self.completo = values_array[3]
        self.data = values_array[4]
        self.periodo = values_array[5]

    @property
    def nome(self):
        return self.__nome
    @nome.setter
    def nome(self,value:str):
        if not isinstance(value,str):
            return
        self.__nome = value
        value = unidecode(value)
        if value.__contains__(TiposAtividade.Domestica):
            self.tipo_atividade = TiposAtividade.Domestica
        elif value.__contains__(TiposAtividade.Descanso):
            self.tipo_atividade = TiposAtividade.Descanso
        else:
            self.tipo_atividade = TiposAtividade.Estudo
        

    @property
    def data(self):
        return self.__data
    @property
    def data_str(self):
        return self.__data.strftime("%d/%m/%Y")
    
    @data.setter
    def data(self,value):
        if isinstance(value,date):
            self.__data = value
            return
        self.__data = datetime.strptime(value,"%d/%m/%Y").date()

    @property
    def duracao(self):
        if not self.__duracao:
            return
        return self.__duracao
    
    @property
    def duracao_str(self):
        return self.__duracao.strftime("%H:%M:%S")
    
    @duracao.setter
    def duracao(self,value:str|datetime):
        if isinstance(value,datetime):
            self.__duracao = value
            return
        HMS = pattern_HMS.findall(value)
        MS = pattern_MS.findall(value)
        if HMS.__len__() != 0:
            date_str = f"{HMS[0][0]}:{HMS[0][1]}:{HMS[0][2]}"
            self.__duracao = datetime.strptime(date_str,"%H:%M:%S")
            return
        if MS.__len__() != 0:
            date_str = f"00:{MS[0][0]}:{MS[0][1]}"
            self.__duracao = datetime.strptime(date_str,"%H:%M:%S")
    @property
    def duracao_time_timedelta(self)->timedelta:
        """Retorna somente o H:M:S ao timedelta"""
        return timedelta(hours=self.duracao.hour,minutes=self.duracao.minute,seconds=self.duracao.second)