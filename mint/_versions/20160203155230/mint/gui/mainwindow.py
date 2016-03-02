import os

from PySide.QtCore import *
from PySide.QtGui import *

from scene import Scene
from view import View
from components import Host

class Mainwindow(QMainWindow):

    def __init__(self, sim, gui_option):
        super(Mainwindow, self).__init__()
        self.sim = sim
        self.scene = Scene(self.sim.entities)
        self.view = View(sim, gui_option, self.scene)
        self.setWindowTitle('mint - Press ? for help')
        path = QApplication.instance().resources['path']
        self.setWindowIcon(QIcon(os.path.join(path, 'pics/logo.ico')))
        self.scene.load()

        lt = QHBoxLayout()
        lt.addWidget(self.view)
        w = QWidget()
        w.setLayout(lt)
        self.setCentralWidget(w)
        self.resize(800, 480)

    def closeEvent(self, ev):
        self.scene.save()
