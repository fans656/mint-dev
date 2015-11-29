import os, re, json, itertools, logging
from collections import OrderedDict
from mint.utils import each

log = logging.getLogger('topology')

class Topology(object):

    def __init__(self, view, items, path='.'):
        self.view = view
        self.items = items
        self.path = path
        self.name = self.gen_name()
        self.fpath = os.path.join(self.path, self.name)

    def gen_name(self):
        roles = [m.role for m in each(self.items).model]
        name = ' '.join('{}{}'.format(len(tuple(g)), role.lower())
                        for role, g in itertools.groupby(sorted(roles)))
        return name + '.topo'

    def save(self):
        item_states = []
        for item in self.items:
            model = item.model
            pos = item.scenePos()
            console_offset = item.console_offset
            console_size = item.console_size
            item_state = OrderedDict((
                ('role', model.role),
                ('index', model.index),
                ('x', pos.x()),
                ('y', pos.y()),
                ('console', OrderedDict((
                    ('dx', console_offset.x()),
                    ('dy', console_offset.y()),
                    ('width', console_size.width()),
                    ('height', console_size.height()),
                    ('enabled', item.console.enabled),
                    ('has_frame', item.console.has_frame),
                    ('visible', item.console.visible),
                ))),
            ))
            item_states.append(item_state)
        info = OrderedDict((
            ('view', {'mode': self.view.mode}),
            ('items', item_states),
        ))
        json.dump(info, open(self.fpath, 'w'), indent=4)

    def load(self):
        if not os.path.exists(self.fpath):
            return False
        info = json.load(open(self.fpath))
        item_states = info['items']
        for state, item in zip(item_states, self.items):
            model = item.model
            if not (state['role'] == model.role and
                    state['index'] == model.index):
                return False
        for state, item in zip(item_states, self.items):
            console_state = state['console']
            console = item.console
            console.moveBy(console_state['dx'], console_state['dy'])
            console.resize(console_state['width'], console_state['height'])
            console.enabled = console_state['enabled']
            console.visible = console_state['visible']
            console.has_frame = console_state['has_frame']
            item.setPos(state['x'], state['y'])
        self.view.mode = info['view']['mode']
        return True
