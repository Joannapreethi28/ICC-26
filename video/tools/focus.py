"""Bring the Chrome window whose title contains a keyword to the front, maximised (and optionally full screen with F11).
python focus.py "ChatGPT" [--f11]   -> prints the matched title, or 'NOT FOUND'
"""
import ctypes
import sys
import time
from ctypes import wintypes

u = ctypes.windll.user32
kw = sys.argv[1].lower()
found = []


@ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
def cb(h, _):
    if u.IsWindowVisible(h):
        n = u.GetWindowTextLengthW(h)
        b = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, b, n + 1)
        t = b.value
        if kw in t.lower() and t.endswith("Google Chrome") and "slides" not in t.lower():
            found.append((h, t))
    return True


u.EnumWindows(cb, 0)
if not found:
    print("NOT FOUND")
    sys.exit(1)
h, t = found[0]
u.ShowWindow(h, 3)  # SW_MAXIMIZE
u.keybd_event(0x12, 0, 0, 0); u.keybd_event(0x12, 0, 2, 0)  # Alt tap lets SetForegroundWindow succeed
u.SetForegroundWindow(h)
time.sleep(0.6)
if "--f11" in sys.argv:
    u.keybd_event(0x7A, 0, 0, 0); u.keybd_event(0x7A, 0, 2, 0)
    time.sleep(1.5)
print("FRONT:", t)
