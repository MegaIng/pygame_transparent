from ctypes.wintypes import RGB

import pygame as pg

from pygame_transparent.trans_base import Transparent
import ctypes
from ctypes import windll, WINFUNCTYPE
from ctypes import wintypes

prototype = WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,
    wintypes.COLORREF,
    wintypes.BYTE,
    wintypes.DWORD
)
paramflags = (1, "hwnd"), (1, "crKey"), (1, "bAlpha"), (1, "dwFlags")
SetLayeredWindowAttributes = prototype(("SetLayeredWindowAttributes", windll.user32), paramflags)

prototype = WINFUNCTYPE(
    wintypes.LONG,
    wintypes.HWND,
    ctypes.c_int,
    wintypes.LONG,
)
paramflags = (1, "hwnd"), (1, "nIndex"), (1, "dwNewLong")
SetWindowLongA = prototype(("SetWindowLongA", windll.user32), paramflags)

prototype = WINFUNCTYPE(
    wintypes.LONG,
    wintypes.HWND,
    ctypes.c_int,
)
paramflags = (1, "hwnd"), (1, "nIndex")
GetWindowLongA = prototype(("GetWindowLongA", windll.user32), paramflags)

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000

LWA_ALPHA = 0x2
LWA_COLORKEY = 0x1


class WindowsTransparent(Transparent):
    _hwnd: int = None
    _overlay: pg.Surface = None
    _old_extstyle: int = None

    def setup(self):
        self._overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA, self.screen)
        self._hwnd = pg.display.get_wm_info()["window"]
        self._old_extstyle = GetWindowLongA(self._hwnd, GWL_EXSTYLE)
        SetWindowLongA(self._hwnd, GWL_EXSTYLE, self._old_extstyle | WS_EX_LAYERED)
        SetLayeredWindowAttributes(self._hwnd, RGB(*self.invis_color), 0, LWA_COLORKEY)

    def reset(self):
        SetLayeredWindowAttributes(self._hwnd, 0, 0, 0)
        SetWindowLongA(self._hwnd, GWL_EXSTYLE, self._old_extstyle)
        self._overlay = None

    def update(self):
        if self._overlay is None:
            raise ValueError("setup() needs to be called before update()")
        if self.dirty:
            if self.dirty < 0:
                self.dirty = 0
                self._overlay.fill((0, 0, 0, 0))
            for r in self.invis_rects[self.dirty:]:
                self._overlay.fill(self.invis_color, r)
            self.dirty = 0
        self.screen.blit(self._overlay, (0, 0))
