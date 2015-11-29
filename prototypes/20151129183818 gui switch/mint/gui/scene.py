import os, logging

from PySide.QtCore import *
from PySide.QtGui import *

from components import Device, Link, create
from topology import Topology
from mint.utils import each

log = logging.getLogger('scene')

class Scene(QGraphicsScene):

    def __init__(self, models):
        super(Scene, self).__init__()
        self.setSceneRect(-4000, -4000, 8000, 8000)
        self.populate(models)

    def populate(self, models):
        self.devices = []
        self.links = []
        self.items = []
        tip2device = {}
        for model in models:
            item = create(model)
            if item:
                log.debug('adding {}'.format(model))
                self.items.append(item)
                if isinstance(item, Device):
                    log.debug('update {}\'s tips'.format(model))
                    tip2device.update({tip: item for tip in model.tips})
                    self.devices.append(item)
                elif isinstance(item, Link):
                    item.setZValue(-1)
                    self.links.append(item)
        log.debug('adding finished: {}'.format(
            map(str, each(self.items).model)))
        self.load_ok = True
        for link in self.links:
            peers = each(link.model.tips).peer
            try:
                link.devices = tuple(tip2device[tip] for tip in peers)
            except KeyError:
                log.error('{}\'s endpoint is not added to scene'.format(
                    link.model))
                self.ok = False
        if self.load_ok:
            for item in self.items:
                self.addItem(item)
                self.addItem(item.console)

    def load(self):
        path = QApplication.instance().resources['path']
        self.topo_path = os.path.join(path, 'topos')
        if self.load_ok:
            ok = Topology(self.views()[0], self.items, self.topo_path).load()
            self.views()[0].load_ok = ok

    def save(self):
        if self.load_ok:
            Topology(self.views()[0], self.items, self.topo_path).save()

    def update_status(self):
        each(self.items).refresh()

    def toggle(self, what):
        each(self.items).toggle(what)
