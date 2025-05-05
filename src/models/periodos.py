from unidecode import unidecode

class Periodo:
    Todos = "Todos"
    Manha = "Manhã"
    Tarde = "Tarde"
    Noite = "Noite"
    __manha_unidecode = unidecode(Manha.lower())
    __tarde_unidecode = unidecode(Tarde.lower())
    __noite_unidecode = unidecode(Noite.lower())
    __todos_unidecode = unidecode(Todos.lower())
    @staticmethod
    def search_periodo(text:str):
        text = unidecode(text.lower())
        if text.__contains__(Periodo.__manha_unidecode):
            return Periodo.Manha
        if text.__contains__(Periodo.__tarde_unidecode):
            return Periodo.Tarde
        if text.__contains__(Periodo.__noite_unidecode):
            return Periodo.Noite
        if text.__contains__(Periodo.__todos_unidecode):
            return Periodo.Todos