import logging, traceback
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import QWebView
from jinja2 import Template
from mint.utils import each

log = logging.getLogger('console')

status_template = Template('''
<style>
* {
    font-size: 11;
    font-family: Consolata;
}
</style>
<pre>{{data|e}}</pre>
''')

class LogView(QTextEdit):

    def __init__(self, stdout):
        super(LogView, self).__init__()
        self.stdout = stdout
        self.refresh()

    def refresh(self):
        self.setText('\n'.join(self.stdout))

class StatusView(QWebView):

    def __init__(self, model):
        super(StatusView, self).__init__()
        self.model = model
        page = self.page()
        page.mainFrame().setScrollBarPolicy(
            Qt.Vertical, Qt.ScrollBarAlwaysOff)
        page.mainFrame().setScrollBarPolicy(
            Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.resize(page.mainFrame().contentsSize())

    def refresh(self):
        status = get_status(self.model)
        s = status_template.render(data=stringify(status))
        self.setHtml(s)

class Console(QGraphicsProxyWidget):

    def __init__(self, item, model):
        super(Console, self).__init__()
        self.model = model
        self._enabled = False
        self._has_frame = True

        self.setVisible(False)
        self.setWindowFlags(Qt.Tool)
        self.setZValue(-3)
        self.tab_container = QTabWidget()
        self.tab_container.setWindowTitle(str(model))
        self.tab_container.currentChanged.connect(self.refresh_tab)

        status = get_status(self.model)
        if isinstance(status, list):
            names = [t[0] for t in status]
            models = [t[1] for t in status]
        else:
            names = ['Status']
            models = [self.model]
        self.views = [StatusView(model) for model in models]
        # add the log tab (read model.stdout)
        logview = LogView(self.model.stdout)
        self.views[0:0] = [logview]
        names[0:0] = [str(self.model)]
        for view, name in zip(self.views, names):
            self.tab_container.addTab(view, name)
        self.setWidget(self.tab_container)
        self.refresh()

    def refresh(self):
        self.refresh_tab(self.tab_container.currentIndex())

    def refresh_tab(self, index):
        self.views[index].refresh()

    def closeEvent(self, ev):
        self._enabled = False
        super(Console, self).closeEvent(ev)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, val):
        self._enabled = val
        if self._enabled:
            self.show()
        else:
            self.close()

    @property
    def visible(self):
        return self.isVisible()

    @visible.setter
    def visible(self, val):
        if self.enabled:
            self.setVisible(val)

    @property
    def has_frame(self):
        return self._has_frame

    @has_frame.setter
    def has_frame(self, val):
        self._has_frame = val
        self.setWindowFlags(Qt.Tool if self.has_frame else Qt.ToolTip)

def stringify(status, depth=0):
    s = ''
    pairs = status.items() if isinstance(status, dict) else status
    for k, v in pairs:
        indent = ' ' * 4 * depth
        if hasattr(v, 'status') or hasattr(type(v), 'status'):
            s += indent + '{}\n'.format(k)
            s += stringify(get_status(v), depth + 1)
        elif isinstance(v, dict):
            s += indent + '{}\n'.format(k)
            s += stringify(v, depth + 1)
        else:
            s += indent + '{}: {}\n'.format(k, v)
    return s

def get_status(model):
    if isinstance(model, dict):
        return model
    try:
        return model.status
    except Exception as e:
        traceback.print_exc()
        log.error('{}.status error {}'.format(model, e))
        return {str(model): 'error getting status'}
