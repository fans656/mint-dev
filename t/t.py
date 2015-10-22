from PySide.QtCore import *
from PySide.QtGui import *

app = QApplication([])

class Widget(QDialog):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        from networking import Thread
        import networking
        self.thread = Thread()
        networking.thread = self.thread
        self.thread.dataReceived.connect(self.dataReceived)
        self.thread.start()
        self.data = ''
        font = self.font()
        font.setPointSize(62)
        self.setFont(font)

    def reject(self):
        from twisted.internet import reactor
        reactor.stop()
        self.thread.quit()
        self.thread.wait()
        self.done(0)

    def dataReceived(self, data):
        self.data = data
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.drawText(self.rect(), Qt.AlignCenter, str(self.data))

w = Widget()
w.show()

app.exec_()
