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
        self.view = View(sim, self.scene)
        self.setWindowTitle('mint')
        self.scene.load()

        lt = QHBoxLayout()
        lt.addWidget(self.view)
        w = QWidget()
        w.setLayout(lt)
        self.setCentralWidget(w)
        self.resize(800, 480)

    def closeEvent(self, ev):
        self.scene.save()
