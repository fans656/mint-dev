import ctypes
import win32api
import win32gui
import win32con
import win32process

def task_windows():

    def f(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        if win32gui.GetParent(hwnd):
            return
        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
            return
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return
        windows.append((hwnd, title))

    windows = []
    win32gui.EnumWindows(f, None)
    return windows[:-1]

def vk2name(vk, vks={}):
    if not vks:
        vks.update({
            getattr(win32con, t): t
            for t in dir(win32con) if t.startswith('VK')
        })
    try:
        return vks[vk]
    except KeyError:
        return chr(vk)
