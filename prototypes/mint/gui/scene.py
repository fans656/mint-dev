import os, logging

from PySide.QtCore import *
from PySide.QtGui import *

from components import Device, Link, create
from topology import Topology

class Scene(QGraphicsScene):

    def __init__(self, models):
        super(Scene, self).__init__()
        self.populate(models)

    def populate(self, models):
        devices = []
        links = []
        tip2device = {}
        for model in models:
            item = create(model)
            if item:
                self.addItem(item)
                if isinstance(item, Device):
                    tip2device.update({tip: item for tip in model.tips})
                    devices.append(item)
                elif isinstance(item, Link):
                    item.setZValue(-1)
                    links.append(item)
        for link in links:
            link.devices = tuple(tip2device[tip.peer]
                                 for tip in link.model.tips)
        self.devices = devices
        self.links = links
        self.items = devices + links
        # try load topology
        path = QApplication.instance().resources['path']
        self.topo_path = os.path.join(path, 'topos')
        Topology(self.items, self.topo_path).load()

    def save(self):
        topo = Topology(self.items, self.topo_path)
        topo.save()
        logging.info('Topology saved to {}'.format(topo.fpath))
