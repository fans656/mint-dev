from PySide.QtCore import *
from PySide.QtGui import *
from f6 import each

class Device(QGraphicsPixmapItem):

    def __init__(self, model):
        cls = type(self)
        if not hasattr(cls, 'pic'):
            app = QApplication.instance()
            pics = app.resources['pics']
            cls.pic = pics.get(cls.__name__, pics['default'])
        super(Device, self).__init__(cls.pic)
        self.model = model
        self.links = []
        self.setOffset(-self.pixmap().width() / 2.0,
                       -self.pixmap().height() / 2.0)
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemSendsGeometryChanges)

    def boundingRect(self):
        return super(Device, self).boundingRect().adjusted(0, 0, 0, 20)

    def paint(self, p, *args):
        super(Device, self).paint(p, *args)
        p.drawText(self.boundingRect(), Qt.AlignBottom | Qt.AlignHCenter,
                   str(self.model))

    def itemChange(self, change, val):
        if change == self.ItemPositionHasChanged:
            each(self.links).track_device()
        return super(Device, self).itemChange(change, val)

class Host(Device):

    def __init__(self, model):
        super(Host, self).__init__(model)
        self.model = model

class Link(QGraphicsLineItem):

    def __init__(self, model):
        super(Link, self).__init__()
        self.model = model
        self._devices = None

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, val):
        self._devices = val
        each(self._devices).links.append(self)
        self.track_device()

    def track_device(self):
        line = QLineF(*each(self.devices).scenePos())
        self.setLine(line)

def create(model):
    try:
        role = type(model).role
        if role in ('Host', 'Link'):
            return eval(role)(model)
    except AttributeError:
        pass
    return None
