import os, inspect

from PySide.QtCore import *
from PySide.QtGui import *

from mainwindow import Mainwindow

def load_pics(path):
    ret = {}
    for fname in os.listdir(path):
        name = os.path.splitext(fname)[0]
        pixmap = QPixmap(os.path.join(path, fname)).scaledToWidth(
            50, Qt.SmoothTransformation)
        ret[name] = pixmap
    return ret

def load_resources():
    ret = {}
    path = os.path.dirname(inspect.getfile(inspect.currentframe()))
    ret['path'] = path
    ret['pics'] = load_pics(os.path.join(path, 'pics'))
    return ret

def run(sim):
    app = QApplication([])
    app.resources = load_resources()
    w = Mainwindow(sim)
    if 1:
        w.showMaximized()
    else:
        w.setGeometry(QStyle.alignedRect(
            Qt.LeftToRight, Qt.AlignCenter,
            w.size(), app.desktop().availableGeometry()
        ))
        w.show()
    app.exec_()
