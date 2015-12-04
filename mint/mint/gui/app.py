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
    pics = load_pics(os.path.join(path, 'pics'))
    pics['frame'] = pics['frame'].scaledToWidth(16)
    ret['pics'] = pics
    return ret

def run(sim, gui_option, *args, **kwargs):
    app = QApplication([])
    font = app.font()
    font.setFamily('Consolas')
    font.setPointSize(8)
    app.setFont(font)
    app.resources = load_resources()
    w = Mainwindow(sim, gui_option, *args, **kwargs)
    if 1:
        w.showMaximized()
    else:
        w.setGeometry(QStyle.alignedRect(
            Qt.LeftToRight, Qt.AlignCenter,
            w.size(), app.desktop().availableGeometry()
        ))
        w.show()
    app.exec_()
