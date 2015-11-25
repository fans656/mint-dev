from PySide.QtCore import *
from PySide.QtGui import *

from scene import Scene
from view import View
from components import Host

class Mainwindow(QMainWindow):

    def __init__(self, sim, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.sim = sim
        self.scene = Scene(self.sim.entities)
        self.view = View(self.scene)

        lt = QHBoxLayout()
        lt.addWidget(self.view)
        w = QWidget()
        w.setLayout(lt)
        self.setCentralWidget(w)

    def closeEvent(self, ev):
        self.scene.save()
