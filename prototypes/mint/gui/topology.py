import os, re, itertools
from f6 import each

class Topology(object):

    def __init__(self, items, path='.'):
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
        with open(self.fpath, 'w') as f:
            for item in self.items:
                model = item.model
                pos = item.scenePos()
                f.write('{} {}: {:.6f} {:.6f}\n'.format(
                    model.role, model.index, pos.x(), pos.y()))

    def load(self):
        if not os.path.exists(self.fpath):
            return False
        pts = []
        for line, item in zip(open(self.fpath), self.items):
            pat = r'(\w+) (\d+): (-?\d+.\d+) (-?\d+.\d+)'
            role, index, x, y = re.match(pat, line.strip()).groups()
            index = int(index)
            model = item.model
            if not (role == model.role and index == model.index):
                return False
            x, y = float(x), float(y)
            pts.append((x, y))
        for pt, item in zip(pts, self.items):
            item.setPos(*pt)
        return True
