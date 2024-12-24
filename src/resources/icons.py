from pathlib import Path
from PyQt6.QtGui import QIcon



common_path = Path("src/resources/")
class Icons:
    obj = None
    def __init__(self):
        if Icons.obj != None:
            return Icons.obj
        self.ClosedEye  = QIcon(common_path.__str__()+"/close-eye.png")
        self.OpenedEye = QIcon(common_path.__str__() +"/open-eye.png")
        self.Hammer = QIcon(common_path.__str__() +"/hammer.png")
        self.House = QIcon(common_path.__str__() +"/house.png")
        self.SleepWhite = QIcon(common_path.__str__() +"/sleep-white.png")
        self.SleepDark = QIcon(common_path.__str__() +"/sleep.png")
        self.circleDark = QIcon(common_path.__str__()+"/circle-dark.png")
        self.taskDone = QIcon(common_path.__str__()+"/task-doned.png")
        self.taskUndone = QIcon(common_path.__str__()+"/task-undoned.png")
        self.appIcon = QIcon(common_path.__str__()+"/app-icon.png")
        self.obj = self
