from datetime import datetime
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

pattern_atividade_manual = cmp(r"(\d\d:\d\d) (\w+) ([^\n]+)")



class MyGoogleEngine:
    LISTA_DE_ATIVIDADES_TASKLIST_ID = "N2JrUXpKRS1JQV9kU0tOSw"
    TASKLIST_CONLUIDAS_ID = "ajNpWjRMVHhrd0s1TGFiVQ"

    def __init__(self):
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
        self.db = Db()

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
            obj.nome = obj.materia + " "+pattern_match[0][2]

    def __get_periodo_with_task_note(self,task_note:str)->str | None:
        """Se nenhum período for reconhecido na nota da task,\n
        nada sera retornado(None)"""
        if task_note.lower().__contains__(Periodo.Manha):
            return Periodo.Manha
        if task_note.lower().__contains__(Periodo.Tarde):
            return Periodo.Tarde
        if task_note.lower().__contains__(Periodo.Noite):
            return Periodo.Noite
        if task_note.lower().__contains__(Periodo.Todos):
            return Periodo.Todos
        return None

    def __make_atividade_by_task(self,task:dict) ->AtividadeItem:
        atividade_obj = AtividadeItem()
        atividade_obj.google_id = task["id"]
        atividade_obj.google_etag = task["etag"]
        atividade_obj.completo = True if task["status"] == "completed" else False
        if task.__contains__("notes"):
            periodo_task_note = self.__get_periodo_with_task_note(task["notes"])
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
        self.db.update(google_obj)

    def __atividade_is_modified(self,db_obj:AtividadeItem,task):
        return isinstance(db_obj,AtividadeItem) and db_obj.google_etag != task["etag"]
    
    def __pass_task_to_tasklist_completeds(self,taskId):
        self.service.tasks().move(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,task=taskId,destinationTasklist=MyGoogleEngine.TASKLIST_CONLUIDAS_ID).execute()

    def sync_database(self):
        all_tasks:dict[dict] = self.service.tasks().list(tasklist=MyGoogleEngine.LISTA_DE_ATIVIDADES_TASKLIST_ID,showHidden=True).execute()["items"]
        for task in all_tasks:
            db_obj = self.db.get_by_google_id(task["id"])

            if self.__atividade_is_modified(db_obj,task):
                self.__update_atividade_modificada(task,db_obj)

            if db_obj == None:
                atividade_obj = self.__make_atividade_by_task(task)
                self.db.add(atividade_obj)
            
            if task["status"] == "completed":
                self.__pass_task_to_tasklist_completeds(task["id"])


