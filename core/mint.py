import os
import functools
import imp

def load(proj_path='.'):
    return Project(proj_path)

class Project(object):

    def __init__(self, path):
        self.path = path
        # load components
        self.components = {}
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, 'components')
        for cname in os.listdir(path):
            cpath = os.path.join(path, cname)
            cfile = os.path.join(cpath, cname + '.py')
            module = imp.load_source(cname, cfile)
            #self.components[module] =

    def __repr__(self):
        return '<mint.Project at {}>'.format(os.path.abspath(self.path))
