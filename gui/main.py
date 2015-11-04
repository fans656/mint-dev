from PySide.QtCore import *
from PySide.QtGui import *

from scene import Scene

app = QApplication([])

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # toolbox
        self.createToolBox()

        # view & scene
        self.scene = Scene(self)

        self.view = QGraphicsView(self.scene)
        self.view.setAcceptDrops(True)

        # layout
        layout = QHBoxLayout()
        layout.addWidget(self.toolBox)
        layout.addWidget(self.view)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # consoles' communication thread
        import communication
        from communication import Thread
        import comm_rpyc
        self.thread = Thread()
        communication.thread = self.thread
        communication.wnd = self
        self.thread.dataReceived.connect(self.dataReceived)
        self.thread.start()

    def dataReceived(self, data):
        self.setWindowTitle(data)

    def closeEvent(self, e):
        pass
        #from twisted.internet import reactor
        #reactor.stop()
        #self.thread.quit()
        #self.thread.wait()

    def createToolBox(self):
        self.toolBox = QToolBox()
        from components import load_component_prototypes, COMPONENT_CATEGORIES
        prototypes_dct = load_component_prototypes()
        for category in COMPONENT_CATEGORIES:
            layout = QGridLayout()
            try:
                prototypes = prototypes_dct[category]
            except KeyError:
                continue
            for i, prototype in enumerate(prototypes):
                layout.addWidget(self.createCellWidget(prototype), i // 2, i % 2)
            tab = QWidget()
            tab.setLayout(layout)
            self.toolBox.addItem(tab, category)
        self.toolBox.setMinimumWidth(tab.sizeHint().width())

    def createCellWidget(self, prototype):
        button = QPushButton()
        icon = QIcon(prototype.icon_path)
        button.setIcon(icon)
        button.setIconSize(QSize(100, 100))
        button.data = prototype
        if prototype.category == 'Devices':
            button.pressed.connect(self.deviceCreationButtonPressed)
        elif prototype.category == 'Links':
            button.pressed.connect(self.linkCreationButtonPressed)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(prototype.name), 1, 0, Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def deviceCreationButtonPressed(self):
        button = self.sender()
        drag = QDrag(self)
        mime = QMimeData()
        mime.data = button.data
        drag.setMimeData(mime)
        drag.setPixmap(button.icon().pixmap(50, 50))
        drag.setHotSpot(QPoint(25, 25))
        drag.exec_()

    def linkCreationButtonPressed(self):
        self.scene.linking = True

w = MainWindow()
w.setGeometry(500, 100, 800, 500)
w.show()

app.exec_()
