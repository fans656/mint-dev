import logging
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

    def __init__(self, model):
        super(Console, self).__init__()
        self.model = model
        self._enabled = False
        self._has_frame = True

        self.setVisible(False)
        self.setWindowFlags(Qt.Tool)
        self.setZValue(-3)
        self.tab_container = QTabWidget()
        self.tab_container.setWindowTitle(str(model))

        status = get_status(self.model)
        if isinstance(status, list):
            names = [t[0] for t in status]
            models = [t[1] for t in status]
        else:
            names = ['Status']
            models = [self.model]
        self.views = [StatusView(model) for model in models]
        for view, name in zip(self.views, names):
            self.tab_container.addTab(view, name)
        self.setWidget(self.tab_container)
        self.refresh()

    def refresh(self):
        each(self.views).refresh()

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
    for k, v in status.items():
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
    r = {str(model): 'has no status'}
    try:
        return getattr(
            model, 'status', r
        )
    except Exception as e:
        log.error('{}.status error {}'.format(model, e))
        return r
