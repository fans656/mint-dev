import threading
import timpy

class Network(object):

    def __init__(self):
        self.env = timpy.Environment()
        self.components = []
        self.threads = []

    def add(self, *components):
        self.components.extend(components)

    def add_thread(self, f):
        thread = threading.Thread(target=f)
        thread.daemon = False
        self.threads.append(thread)

    def run(self, *args, **kwargs):
        for component in self.components:
            if hasattr(component, 'run'):
                self.env.process(component.run, name=str(component))
        for thread in self.threads:
            thread.start()
        self.env.run(
                terminate=lambda: all(not t.is_alive() for t in self.threads),
                *args, **kwargs)

network = Network()
