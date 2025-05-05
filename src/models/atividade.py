from dataclasses import dataclass
from datetime import datetime,date, timedelta
import datetime as dt
from re import compile as cmp
from src.models.tipos_atividade import TiposAtividade
from src.models.periodos import Periodo
from unidecode import unidecode
from src.models.materias import Materias
pattern_HMS = cmp(r"(\d\d):(\d\d):(\d\d)")
pattern_MS = cmp(r"(\d\d):(\d\d)")


class AtividadeItem:
    """
    Esta classe está destinada para guardar informações de uma atividade qualquer.
    # atributos
    - id
    - periodo
    - data
    - materia: Leia a [[Observação]] abaixo
    - google_id
    - google_etag

    # propriedades
    - nome: É uma propriedade, pois quando recebe um valor, ela define também "tipo_atividade"
    - duração: É uma propriedade, pois pode receber valores string, com formato "H:M:S" ou datetime
    - tipo_atividade: Propriedade definida pelo **nome**, toda vez que instanciada

    # Observação
    Como a verificação de matéria para objeto é custosa, ela somente é verificada ao ser atualizada no banco de dados
    ou quando é inserida, pelo AtividadeInputLineEdit
    """
    
    def __init__(self):
        self.id:int = 0
        self.__nome:str = None
        self.__duracao:datetime = None
        self.completo:bool = False
        self.periodo:str
        self.__data:datetime = None
        self.tipo_atividade = None
        self.__materia = None
        self.__google_id:str = None
        self.__google_etag:str =  None

    def set_values_by_array(self,values_array):
        self.id = values_array[0]
        self.nome = values_array[1]
        self.duracao = values_array[2]
        self.completo = values_array[3]
        self.data = values_array[4]
        self.periodo = values_array[5]
        self.materia = values_array[6]
        self.__google_id = values_array[7]
        self.__google_etag = values_array[8]


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
    def data(self,value:str):
        if isinstance(value,date):
            self.__data = value
            return
        if value.__len__()>10: # quer dizer que está no formato do google tasks no atributo due
            self.__data = datetime.fromisoformat(value).date()
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
    
    @property
    def materia(self):
        return self.__materia
    
    @materia.setter
    def materia(self,value:str):
        if not isinstance(value,str):
            self.__materia = Materias.Geral
            return
        
        self.__materia = Materias.searchMateria(value)

    @property
    def google_id(self):
        return self.__google_id
    
    @google_id.setter
    def google_id(self,value):
        if not isinstance(self.__google_id,str):
            self.__google_id = value
            return
        raise AttributeError("Google Id não pode alterado")



    @property
    def google_etag(self):
        return self.__google_etag
    
    @google_etag.setter
    def google_etag(self,value):
        self.__google_etag = value

    def to_task(self)->dict:
        task = {
        "title": f"{self.duracao_str} {self.nome}",
        "notes": f"Período:{self.periodo}",
        "due": f"{self.data.isoformat()}T00:00:00Z"
        }
        if self.completo:
            task["status"] = "completed"
        if self.google_id != None:
            task["id"] = self.google_id
        return task



        