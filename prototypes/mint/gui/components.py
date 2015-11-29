import logging
from PySide.QtCore import *
from PySide.QtGui import *
from misc import Console
from mint.utils import each

log = logging.getLogger('component')

def create(model):
    try:
        role = type(model).role
    except AttributeError:
        log.warning('{} got no role'.format(model))
    else:
        if role in ('Host', 'Hub', 'Switch', 'Router', 'Link'):
            return eval(role)(model)
    return None

class Model(object):

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(Model, self).__init__(*args, **kwargs)
        self.console = Console(model)
        self.setToolTip(str(self.model))

    @property
    def console_offset(self):
        return self.console.scenePos() - self.scenePos()

    @property
    def console_size(self):
        return self.console.size()

    def mouseDoubleClickEvent(self, ev):
        self.console.enabled = not self.console.enabled

    def toggle(self, what):
        if what == 'console enabled':
            self.console.enabled = not self.console.enabled
        elif what == 'console visible':
            self.console.visible = not self.console.visible
        elif what == 'console frame':
            self.console.has_frame = not self.console.has_frame

    def refresh(self):
        self.console.refresh()

    def itemChange(self, change, val):
        if change == QGraphicsItem.ItemPositionChange:
            val = super(Model, self).itemChange(change, val)
            offset = val - self.pos()
            self.console.moveBy(offset.x(), offset.y())
            return val
        return super(Model, self).itemChange(change, val)

class Device(Model, QGraphicsPixmapItem):

    def __init__(self, model):
        super(Device, self).__init__(model, self.pic)
        self.links = []
        self.setOffset(-self.pixmap().width() / 2.0,
                       -self.pixmap().height() / 2.0)
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemSendsGeometryChanges)

    @property
    def pic(self):
        cls = type(self)
        while True:
            try:
                return cls._pic
            except AttributeError:
                pics = QApplication.instance().resources['pics']
                cls._pic = pics.get(cls.__name__, pics['default'])

    def is_sending_to(self, peer):
        try:
            return self.model.is_sending_to(peer.model)
        except Exception as e:
            log.warning(str(e))
            raise
            return False

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

class Switch(Device): pass

class Router(Device): pass

class Link(Model, QGraphicsLineItem):

    def __init__(self, model):
        super(Link, self).__init__(model)
        self._devices = None
        pen = self.pen()
        pen.setWidth(2)
        self.setPen(pen)

    @property
    def console_offset(self):
        return self.console.scenePos() - self.line().pointAt(0.5)

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, val):
        self._devices = val
        each(self._devices).links.append(self)
        self.track_device()

    def track_device(self):
        old_line = self.line()
        new_line = QLineF(*each(self.devices).scenePos())
        old_mid_pt = old_line.pointAt(0.5)
        new_mid_pt = new_line.pointAt(0.5)
        offset = new_mid_pt - old_mid_pt
        self.console.moveBy(offset.x(), offset.y())
        self.setLine(new_line)

    def paint(self, p, *args):
        super(Link, self).paint(p, *args)
        if self.devices[0].is_sending_to(self.devices[1]):
            norm = self.line().normalVector()
            norm_offset = QPointF(norm.dx(), norm.dy()) / norm.length() * 20
            unit = self.line().unitVector()
            unit_offset = QPointF(unit.dx(), unit.dy()) / unit.length() * 20
            beg = self.line().pointAt(0.2)
            beg += norm_offset
            end = beg + unit_offset
            rc = QRectF(end, QSize(5, 5))
            p.drawLine(QLineF(beg, end))
            p.drawRect(rc)
        if self.devices[1].is_sending_to(self.devices[0]):
            norm = self.line().normalVector()
            norm_offset = QPointF(norm.dx(), norm.dy()) / norm.length() * -20
            unit = self.line().unitVector()
            unit_offset = QPointF(unit.dx(), unit.dy()) / unit.length() * -20
            beg = self.line().pointAt(0.8)
            beg += norm_offset
            end = beg + unit_offset
            rc = QRectF(end, QSize(5, 5))
            p.drawLine(QLineF(beg, end))
            p.drawRect(rc)
