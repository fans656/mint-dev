import os
import imp
import sys

from PySide.QtCore import *
from PySide.QtGui import *

class Env(object):

    def load_env(self):
        # load custum scripts
        env = os.path.join(self.device.path, 'env.py')
        sys.path.insert(0, self.device.path)
        env = imp.load_source('', env)
        del sys.path[0]
        env.interfaces = {cls.__name__: cls(self) for cls in env.config['interfaces']}
        self.env = env


class DeviceItem(QGraphicsPixmapItem, Env):

    def __init__(self, device):
        self.device = device
        self.load_env()
        pixmap = QPixmap(device.icon_path).scaledToWidth(100)
        super(DeviceItem, self).__init__(pixmap)
        size = pixmap.size()
        self.setOffset(-size.width() / 2, -size.height() / 2)
        self.draging = False

        self.setFlags(QGraphicsItem.ItemIsSelectable
                | QGraphicsItem.ItemIsMovable
                | QGraphicsItem.ItemIsFocusable
                | QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.links = []

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.scene().removeItem(self)
            del self

    def hoverEnterEvent(self, e):
        if self.scene().linking:
            self.setSelected(True)

    def hoverLeaveEvent(self, e):
        if self.scene().linking:
            self.setSelected(False)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.scene().linking:
            link = self.scene().linkInCreation
            # create link
            if not link:
                self.setSelected(False)
                e.ignore()
                link = LinkItem(self)
                self.links.append(link)
                link.setLine(QLineF(self.scenePos(), e.scenePos()))
                self.scene().addItem(link)
                self.scene().linkInCreation = link
            # finish link
            elif link.source != self:
                link.sink = self
                link.setLine(QLineF(link.line().p1(), self.scenePos()))
                self.links.append(link)
                self.scene().finishLinking()

    def mouseDoubleClickEvent(self, e):
        from communication import host, port
        import communication
        communication.console_object = self
        os.system('start python -i console.py {host} {port} {env}'.format(
            'console.py',
            host=host,
            port=port,
            env=os.path.join(self.device.path, 'env.py'),
            ))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for link in self.links:
                link.updateEndPositions()
        return super(DeviceItem, self).itemChange(change, value)

    def get_peer(self):
        try:
            return self.links[0].env
        except IndexError:
            from communication import NoPeer
            raise NoPeer('No peer')

class LinkItem(QGraphicsLineItem, Env):

    def __init__(self, source):
        if source:
            self.device = source.device
            self.load_env()
        super(LinkItem, self).__init__()
        self.source = source
        self.sink = None
        self.setZValue(-1)
        pen = self.pen()
        pen.setWidth(3)
        self.setPen(pen)
        self.setFlags(QGraphicsItem.ItemIsSelectable)

    def updateEndPositions(self):
        self.setLine(QLineF(self.source.scenePos(),
            self.sink.scenePos()))

    #def get_peer(self):
    #    return pass
