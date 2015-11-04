import os
import imp
from itertools import groupby

from PySide.QtCore import *
from PySide.QtGui import *

COMPONENT_CATEGORIES = ['Devices', 'Links']
DEFAULT_CONFIG = {
        'category': 'Devices',
        'icon': 'icon.png',
        }

class Component(object):

    def __init__(self, path, config):
        self.path = path
        self.name = config['name']
        self.icon_path = os.path.join(path, config['icon'])
        self.category = config['category']

def load_component_prototypes():
    config_files = [os.path.join(path, fname)
            for path, _, fnames in os.walk('components')
            for fname in fnames if fname == 'config.py']
    prototypes = []
    for config_file in config_files:
        try:
            config = DEFAULT_CONFIG.copy()
            config.update(imp.load_source('', config_file).config)
            prototypes.append(Component(os.path.dirname(config_file), config))
        except AttributeError:
            pass
    key = lambda t: t.category
    prototypes = {k: list(g) for k, g in groupby(sorted(prototypes, key=key), key)}
    return prototypes

if __name__ == '__main__':
    app = QApplication([])
    a = load_component_prototypes()
