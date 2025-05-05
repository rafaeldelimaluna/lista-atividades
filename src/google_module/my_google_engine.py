from datetime import datetime
import logging
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pprint import pp
from src.models.atividade import AtividadeItem
from re import compile as cmp,DOTALL
from src.db import Db
from src.models import Periodo,Materias

pattern_atividade_manual = cmp(r"(\d\d:\d\d(?::\d\d)) (\w+) ([^\n]+)")



class MyGoogleEngine:
    LISTA_DE_ATIVIDADES_TASKLIST_ID = "N2JrUXpKRS1JQV9kU0tOSw"
    TASKLIST_CONLUIDAS_ID = "ajNpWjRMVHhrd0s1TGFiVQ"

    def __init__(self,connection:Db):
        CLIENT_FILE = "private.json"
        SCOPES = ['https://www.googleapis.com/auth/tasks']
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)


        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('tasks', 'v1', credentials=creds)
        self.connection = connection

    def add(self,atividade_obj:AtividadeItem)->dict:
        task = atividade_obj.to_task()
        output = self.service.tasks().insert(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,body=task).execute()
        return output
    
    def update(self,atividade_obj:AtividadeItem)->dict:
        # task = self.service.tasks().get(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID).execute()
        task = atividade_obj.to_task()
        
        output = self.service.tasks().update(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,task=atividade_obj.google_id,body=task).execute()
        print(output)
        return output
    
    def remove(self,googleId:str)->None:
        print(f"{googleId=}")
        output = self.service.tasks().delete(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,task=googleId).execute()
        print(output)

    def __inserir_dados_de_title(self,obj:AtividadeItem,title:str)->None:
        """Ele insere os dados por referência, por isso não existe retorno"""
        pattern_match = pattern_atividade_manual.findall(title)
        if pattern_match == []:
            obj.nome = title
            obj.duracao = "00:00"
            obj.materia = Materias.Geral
        else:
            obj.duracao = pattern_match[0][0]
            obj.materia = Materias.searchMateria(pattern_match[0][1])
            obj.nome = pattern_match[0][2]

    def __make_atividade_by_task(self,task:dict) ->AtividadeItem:
        atividade_obj = AtividadeItem()
        atividade_obj.google_id = task["id"]
        atividade_obj.google_etag = task["etag"]
        atividade_obj.completo = True if task["status"] == "completed" else False
        if task.__contains__("notes"):
            periodo_task_note = Periodo.search_periodo(task["notes"])
            atividade_obj.periodo = periodo_task_note if isinstance(periodo_task_note,str) else Periodo.Todos
        else:
            atividade_obj.periodo = Periodo.Todos

        if task.__contains__("due"):
            atividade_obj.data = task["due"]
        else:
            atividade_obj.data = datetime.now().date()
        self.__inserir_dados_de_title(atividade_obj,task["title"])

        return atividade_obj
    
    def __update_atividade_modificada(self,task:dict,db_obj:AtividadeItem):
        google_obj = self.__make_atividade_by_task(task)
        google_obj.id = db_obj.id
        self.connection.update(google_obj)

    def __atividade_is_modified(self,db_obj:AtividadeItem,task):
        return isinstance(db_obj,AtividadeItem) and db_obj.google_etag != task["etag"]
    
    def __pass_task_to_tasklist_completeds(self,taskId):
        self.service.tasks().move(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,task=taskId,destinationTasklist=MyGoogleEngine.TASKLIST_CONLUIDAS_ID).execute()
        
    def __task_is_deleted(self,task:dict)->bool:
        return task.__contains__("deleted") and task["deleted"]
    
    def sync_database(self):
        """Faz a ação de adicionar e dar update das tasks para o banco de dados"""
        all_tasks:dict[dict] = self.service.tasks().list(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,showHidden=True,showDeleted=True).execute()["items"]
        for task in all_tasks:
            db_obj = self.connection.get_by_google_id(task["id"])

            if db_obj == None:
                if self.__task_is_deleted(task):
                    continue
                atividade_obj = self.__make_atividade_by_task(task)
                self.connection.add(atividade_obj)
                continue

            pp(self.__make_atividade_by_task(task).__dict__)

            if self.__atividade_is_modified(db_obj,task):
                if self.__task_is_deleted(task):
                    self.connection.deleteByGoogleId(task["id"])
                else:
                    self.__update_atividade_modificada(task,db_obj)
            
            if task["status"] == "completed":
                self.__pass_task_to_tasklist_completeds(task["id"])


