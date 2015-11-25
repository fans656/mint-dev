from PySide.QtCore import *
from PySide.QtGui import *
from topology import Topology

class View(QGraphicsView):

    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setMinimumSize(480, 480)
        self.setRenderHints(QPainter.Antialiasing)

    def keyPressEvent(self, ev):
        ch = ev.text()
        if ch == ' ':
            pass
