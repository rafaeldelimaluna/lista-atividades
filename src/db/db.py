from datetime import datetime
import logging
from sqlite3 import connect,Connection
from src.models import AtividadeItem
from src.models import Periodo
from typing import overload

class Db:
    connection:Connection = None
    __query_to_insert = "INSERT INTO ATIVIDADES (Nome,Duracao,Completo,Data,Periodo) VALUES (?,?,?,?,?)"
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
            PERIODO TEXT NOT NULL)
        """)
        self.connection.commit()


    def get(self,id:int) -> AtividadeItem|None:
        result = self.connection.execute("SELECT ROWID,* FROM ATIVIDADES WHERE ROWID = ?",[id]).fetchone()
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
            self.connection.execute(Db.__query_to_insert,[atividade_item.nome,atividade_item.duracao_str,atividade_item.completo,atividade_item.data_str,atividade_item.periodo])    
            
        if isinstance(atividade_item,list):
            values = map(lambda atividade_item:[atividade_item.nome,atividade_item.duracao_str,atividade_item.completo,atividade_item.data_str,atividade_item.periodo],atividade_item)
            print(values)
            self.connection.executemany(Db.__query_to_insert,values)
        self.connection.commit()

    def update(self,atividade_item:AtividadeItem):
        if atividade_item.id == 0 or atividade_item.id == None or atividade_item is None:
            logging.warning(f"ATIVIDADE ITEM COM VALORES ESTRANHOS PARA UPDATE: {atividade_item.id=}")
            return
        self.connection.execute("UPDATE ATIVIDADES SET NOME=?,DURACAO=?,COMPLETO=?,Data=?,Periodo=? WHERE ROWID=?",[atividade_item.nome,atividade_item.duracao_str,atividade_item.completo,atividade_item.data_str,atividade_item.periodo,atividade_item.id])
        self.connection.commit()

        
    def deleteByItem(self,atividade_item:AtividadeItem):
        self.deleteById(atividade_item.id) 


    def deleteById(self,atividade_id:int):
        self.connection.execute("DELETE FROM ATIVIDADES WHERE ROWID=?",[atividade_id])
        self.connection.commit()
