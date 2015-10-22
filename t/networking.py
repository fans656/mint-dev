import random
import time

from twisted.internet import protocol, endpoints

from PySide.QtCore import *
from PySide.QtGui import *

thread = None

class Echo(protocol.Protocol):

    def dataReceived(self, data):
        self.transport.write(data)
        thread.dataReceived.emit(data)

class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return Echo()

class Thread(QThread):

    dataReceived = Signal(int)

    def run(self):
        from twisted.internet import reactor
        endpoints.serverFromString(reactor, "tcp:1234").listen(
                EchoFactory())
        reactor.run(False)
        #while True:
        #    time.sleep(random.randint(1,9) / 10.0)
        #    data = [random.randint(1,9)]
        #    self.dataReceived.emit(data)
