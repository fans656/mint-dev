from PySide.QtCore import *
from PySide.QtGui import *

from componentitem import DeviceItem

class Scene(QGraphicsScene):

    def __init__(self, parent=None):
        super(Scene, self).__init__(parent)
        self.setSceneRect(QRectF(0, 0, 480, 480))
        self.linking = False
        self.linkInCreation = None

    def dragEnterEvent(self, e):
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        e.accept()
        pos = e.scenePos()
        component = e.mimeData().data
        item = DeviceItem(component)
        item.setPos(pos)
        self.addItem(item)

    def mouseMoveEvent(self, e):
        if self.linkInCreation:
            link = self.linkInCreation
            link.setLine(QLineF(link.line().p1(), e.scenePos()))
            # fallthrough
        super(Scene, self).mouseMoveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton and self.linking:
            self.finishLinking(True)
            return
        super(Scene, self).mousePressEvent(e)

    def finishLinking(self, delete=False):
        if delete:
            link = self.linkInCreation
            try:
                link.source.links.remove(link)
                link.sink.links.remove(link)
            except AttributeError:
                pass
            self.removeItem(link)
            del link
        self.linking = False
        self.linkInCreation = None
