import env
from misc import new_obj_index

class Obj(object):

    def __init__(self):
        self.obj_index = new_obj_index(self)
        self.env = env.env

    def __repr__(self):
        return '{}{}'.format(type(self).__name__, self.obj_index)
