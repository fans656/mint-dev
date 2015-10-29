from PySide.QtCore import *
from PySide.QtGui import *

thread = None
host = 'localhost'
port = 6560

class Thread(QThread):

    dataReceived = Signal(list)

    def run(self):
        print 'dummy Thread.run'
