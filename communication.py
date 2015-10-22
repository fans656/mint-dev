from twisted.internet import protocol, endpoints

from PySide.QtCore import *
from PySide.QtGui import *

thread = None
host = 'localhost'
port = 1234

class Echo(protocol.Protocol):

    def dataReceived(self, data):
        self.transport.write(data)
        thread.dataReceived.emit(data)

class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return Echo()

class Thread(QThread):

    dataReceived = Signal(list)

    def run(self):
        from twisted.internet import reactor
        endpoints.serverFromString(reactor, "tcp:{}".format(port)).listen(
                EchoFactory())
        reactor.run(False)
