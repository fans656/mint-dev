import logging, functools
from PySide.QtCore import *
from PySide.QtGui import *
from topology import Topology
import config

log = logging.getLogger('view')

class View(QGraphicsView):

    MODE_EVENT = 'Event'
    MODE_TIK_TOK = 'Tik-Tok'
    MODE_PHASE = 'Phase'
    MODES = [MODE_EVENT, MODE_TIK_TOK, MODE_PHASE]

    def __init__(self, sim, parent=None):
        super(View, self).__init__(parent)
        self.sim = sim
        self.setMinimumSize(480, 480)
        self.setRenderHints(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.load_ok = False
        self._mode = self.MODE_EVENT
        self.thread = None

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, val):
        self._mode = val
        self.viewport().update()

    def keyPressEvent(self, ev):
        ch = ev.text()
        if ch == config.key['Step']:
            self.step()
        elif ch == config.key['Toggle console']:
            self.toggle_console()
        elif ch == config.key['Toggle console frame']:
            self.scene().toggle('console frame')
        elif ch == config.key['Toggle mode']:
            self.toggle_mode()
        elif ch == config.key['Next mode']:
            self.next_mode()
        elif ch == config.key['Run']:
            self.run()
        elif ch == '?':
            self.help()

    def run(self):
        if hasattr(self, 'timer'):
            self.stop()
        elif not self.sim.finished:
            self.timer = QTimer()
            self.timer.timeout.connect(self.step_and_refresh)
            self.timer.start(30) # time interval
        else:
            QMessageBox.warning(self, 'Error',
                                'Simulation finished.\n' +
                                'Please restart.')

    def stop(self):
        self.timer.stop()
        del self.timer

    def step_and_refresh(self):
        if self.sim.finished:
            self.stop()
        else:
            self.sim.step()
            self.refresh()

    def step(self):
        sim = self.sim
        if sim.finished and self.mode == self.MODE_EVENT:
            self.mode = self.MODE_TIK_TOK
        if self.mode == self.MODE_EVENT:
            if not self.thread or self.thread.isFinished():
                self.thread = StepUntilSthHappend(sim)
                self.thread.finished.connect(self.refresh)
                self.thread.start()
        elif self.mode == self.MODE_TIK_TOK:
            sim.step()
        elif self.mode == self.MODE_PHASE:
            sim.step(by=sim.Phase)
        else:
            log.error('{} mode not recognized'.format(self.mode))
        self.refresh()

    def refresh(self):
        self.scene().update_status()
        self.viewport().update()

    def toggle_console(self):
        if not self.load_ok:
            self.scene().toggle('console enabled')
            self.load_ok = True
            log.debug('load failed, initial switch consoles\' enabled')
        else:
            self.scene().toggle('console visible')
            log.debug('load ok, just switch consoles\' visibility')

    def next_mode(self, mod=0):
        if not mod:
            mod = len(self.MODES)
        i = (self.MODES.index(self.mode) + 1) % mod
        self.mode = self.MODES[i]
    toggle_mode = lambda self: self.next_mode(mod=2)

    def help(self):
        text = ''
        for role, key in config.key.items():
            text += '{}\t {}\n'.format(key, role)
        QMessageBox.information(self, 'Help', text)

    def drawForeground(self, p, rc):
        p.save()
        font = p.font()
        font.setFamily('Arial')
        font.setPointSize(10)
        p.setFont(font)
        pen = p.pen()
        pen.setColor(QColor(0,0,0,128))
        p.setPen(pen)
        sim = self.sim
        # draw simulation status
        s = ''
        s += 'Mode: {}\n'.format(self.mode)
        s += 'Stat: {}\n'.format(sim.status)
        s += 'Time: {}\n'.format(sim.now)
        p.drawText(rc, Qt.AlignTop | Qt.AlignLeft, s)
        # draw simulation stdout
        s = ''
        for line in sim.stdout:
            s += line + '\n'
        p.drawText(rc, Qt.AlignTop | Qt.AlignHCenter, s)

        p.restore()
        super(View, self).drawForeground(p, rc)

class StepUntilSthHappend(QThread):

    def __init__(self, sim):
        super(StepUntilSthHappend, self).__init__()
        self.sim = sim

    def run(self):
        while True:
            self.sim.step()
            if self.sim.finished or self.sim.stdout:
                break
