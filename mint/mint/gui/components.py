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
        self.console = Console(self, model)
        self.setToolTip(str(self.model))
        self.highlighted = False
        self.stdout_n_lines = 0

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
        n_lines = len(self.model.stdout)
        if n_lines != self.stdout_n_lines:
            self.highlighted = True
            self.stdout_n_lines = n_lines
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

    def boundingRect(self):
        return super(Device, self).boundingRect().adjusted(0, 0, 0, 20)

    def paint(self, p, *args):
        super(Device, self).paint(p, *args)
        if self.highlighted:
            p.drawRect(self.boundingRect())
        p.drawText(self.boundingRect(), Qt.AlignBottom | Qt.AlignHCenter,
                   str(self.model))

    def itemChange(self, change, val):
        if change == self.ItemPositionHasChanged:
            each(self.links).track_device()
        return super(Device, self).itemChange(change, val)

class Host(Device): pass
class Switch(Device): pass
class Router(Device): pass

class Link(Model, QGraphicsLineItem):

    def __init__(self, model):
        super(Link, self).__init__(model)
        self._devices = None
        pen = self.pen()
        pen.setWidth(2)
        self.setPen(pen)
        self.pixmap = QApplication.instance().resources['pics']['frame']
        self.pixmap_half_width = self.pixmap.width() / 2.0
        self.pixmap_half_height = self.pixmap.height() / 2.0

    def setLine(self, *args, **kwargs):
        super(Link, self).setLine(*args, **kwargs)
        line = self.line()
        self.rline = QLineF(line.p2(), line.p1())

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

    # this scheme is wrong
    # it only accounts for the sending frame
    # if link latency is high, the frame travels on the link
    # will be invisible once the sending is over
    def sending_progress(self, device):
        entity = device.model
        link = self.model
        tip = link[entity]
        sending = entity.sending(at=tip)
        if not sending:
            return 0
        return entity.sent(at=tip) / float(sending + link.latency)

    def paint(self, p, *args):
        super(Link, self).paint(p, *args)
        pg0 = self.sending_progress(self.devices[0])
        pg1 = self.sending_progress(self.devices[1])
        if pg0:
            self.draw_arrow(p, pg0, self.line())
        if pg1:
            self.draw_arrow(p, pg1, self.rline)

    def draw_arrow(self, p, ratio, line, length=10):
        line = QLineF(line)
        line.setP2(line.pointAt(1 - length / line.length()))
        pt = QPointF(line.length() * ratio - self.pixmap_half_width,
                     -10 - self.pixmap_half_height)
        p.save()
        p.translate(line.p1())
        p.rotate(-line.angle())
        p.drawPixmap(pt, self.pixmap)
        p.restore()
