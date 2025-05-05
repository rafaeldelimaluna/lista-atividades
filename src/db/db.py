from datetime import datetime
import logging
from sqlite3 import connect,Connection
from src.models import AtividadeItem
from src.models import Periodo
from typing import overload

class Db:
    connection:Connection = None
    __query_to_insert = "INSERT INTO ATIVIDADES (Nome,Duracao,Completo,Data,Periodo,Materia,GOOGLE_ID,GOOGLE_ETAG) VALUES (?,?,?,?,?,?,?,?)"
    def __init__(self):
        if isinstance(Db.connection,Connection):
            self.connection = Db.connection.cursor()
            return
        self.connection = connect("database.db")
        self.__create_table_atividades()


    def __create_table_atividades(self):
        self.connection.execute("""
        CREATE TABLE IF NOT EXISTS ATIVIDADES(
            NOME TEXT NOT NULL,
            DURACAO TEXT NOT NULL,
            COMPLETO BOOL DEFAULT 0,
            DATA TEXT NOT NULL,
            PERIODO TEXT NOT NULL,
            MATERIA TEXT NOT NULL,
            GOOGLE_ID TEXT UNIQUE,
            GOOGLE_ETAG TEXT);""")
        self.connection.execute("CREATE TABLE IF NOT EXISTS ENTRADAS_NO_APP (DATA TEXT NOT NULL);")
        self.connection.commit()


    def get(self,id:int) -> AtividadeItem|None:
        result = self.connection.execute("SELECT ROWID,* FROM ATIVIDADES WHERE ROWID = ?",[id]).fetchone()
        if result == None:
            return
        item = AtividadeItem()
        item.set_values_by_array(result)
        return item
    

    def get_all_white_google_id(self)->list[AtividadeItem]:
        """Retorna todos os objetos que estão com o atributo google_id nulo. \n
        ## OBS:
        Somente serão retornados objetos depois do rowid 420, pois a implementação do google tasks é no dia 5 e este valor corresponde com o dia
         """
        query = f"SELECT ROWID,* FROM ATIVIDADES WHERE GOOGLE_ID IS NULL AND ROWID>420"
        result = self.connection.execute(query).fetchall()
        items:list[AtividadeItem] = list()
        for item in result:
            obj = AtividadeItem()
            obj.set_values_by_array(item)
            items.append(obj)
        return items

        

    def get_by_google_id(self,googleId:str) ->AtividadeItem|None:
        result = self.connection.execute("SELECT ROWID,* FROM ATIVIDADES WHERE GOOGLE_ID = ?",[googleId]).fetchone()
        if result == None:
            return
        item = AtividadeItem()
        item.set_values_by_array(result)
        return item

    def get_all(self,periodo:str=Periodo.Todos,data:datetime = None):
        query:str
        if periodo == Periodo.Todos:
            query = "SELECT ROWID,* FROM ATIVIDADES"
        else:
            query = f"SELECT ROWID,* FROM ATIVIDADES WHERE PERIODO='{periodo}'"
        result = self.connection.execute(query).fetchall()
        items:list[AtividadeItem] = list()
        if data == None:
            for row in result:
                item = AtividadeItem()
                item.set_values_by_array(row)
                items.append(item)
        else:
            for row in result:
                item = AtividadeItem()
                item.set_values_by_array(row)
                if item.data == data:
                    items.append(item)
        return items
    
    def add(self,atividade_item:AtividadeItem | list[AtividadeItem]):
        if isinstance(atividade_item,AtividadeItem):
            self.connection.execute(Db.__query_to_insert,[atividade_item.nome,atividade_item.duracao_str,atividade_item.completo,atividade_item.data_str,atividade_item.periodo,atividade_item.materia,atividade_item.google_id,atividade_item.google_etag])    
            
        if isinstance(atividade_item,list):
            values = []
            for item in atividade_item:
                values.append([item.nome,item.duracao_str,item.completo,item.data_str,item.periodo,item.materia,item.google_id,item.google_etag])
                self.__google_engine.add(item)
            print(values)
            self.connection.executemany(Db.__query_to_insert,values)
        self.connection.commit()


    def update(self,atividade_item:AtividadeItem):
        """No método update, é verificado a mateŕia desta atividade, tendo em vista que é custosa essa verificação"""
        if atividade_item.id == 0 or atividade_item.id == None or atividade_item is None:
            logging.warning(f"ATIVIDADE ITEM COM VALORES ANORMAIS PARA UPDATE: {atividade_item.id=}")
            return
        self.connection.execute("UPDATE ATIVIDADES SET NOME=?,DURACAO=?,COMPLETO=?,Data=?,Periodo=?,MATERIA=?,GOOGLE_ID=?,GOOGLE_ETAG=? WHERE ROWID=?",[atividade_item.nome,atividade_item.duracao_str,atividade_item.completo,atividade_item.data_str,atividade_item.periodo,atividade_item.materia,atividade_item.google_id,atividade_item.google_etag,atividade_item.id])
        self.connection.commit()

        
    def deleteByItem(self,atividade_item:AtividadeItem):
        self.deleteById(atividade_item.id) 


    def deleteById(self,atividade_id:int):
        self.connection.execute("DELETE FROM ATIVIDADES WHERE ROWID=?",[atividade_id])
        self.connection.commit()
    
    def update_last_entry(self):
        """Salva a ultima vez em que o programa. Salva esse dado no banco de dados"""
        white_obj = AtividadeItem()
        white_obj.data = datetime.now().date()
        self.connection.execute("INSERT INTO ENTRADAS_NO_APP(DATA) VALUES(?)",[white_obj.data_str])
        self.connection.commit()
        
    def get_last_entry(self):
        """Retorna a última vez em que o programa foi fechado.
        Tipo: Date"""
        white_obj = AtividadeItem()
        data_str= self.connection.execute("SELECT DATA FROM ENTRADAS_NO_APP ORDER BY ROWID DESC LIMIT 1").fetchone() 
        white_obj.data = data_str[0]
        return white_obj.data
        