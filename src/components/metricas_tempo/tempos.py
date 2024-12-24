from datetime import datetime,timedelta


class Tempos:
    def __init__(self):
        self.descanso = datetime.today().min
        self.estudo = datetime.today().min
        self.domestico = datetime.today().min
    @property
    def total(self):
        estudos_delta = timedelta(hours=self.estudo.hour,minutes=self.estudo.minute,seconds=self.estudo.second)
        domestico_delta = timedelta(hours=self.domestico.hour,minutes=self.domestico.minute,seconds=self.domestico.second)
        result = self.descanso+estudos_delta+domestico_delta
        print(result)
        return result