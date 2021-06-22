import pygame as pg

from pygame_transparent.trans_base import Transparent
from pygame_transparent.xlib import *


class X11Transparent(Transparent):
    _display: int = None
    _window: int = None
    _reg: int = None

    def __init__(self, *args, **kwargs):
        super(X11Transparent, self).__init__(*args, **kwargs)
        self.overlay = pg.display

    def setup(self):
        info = pg.display.get_wm_info()
        self._display = PyCapsule_GetPointer(info["display"], b"display")
        self._window = info["window"]
        if not XShapeQueryExtension(self._display):
            raise RuntimeError("Shape Extension not available")
        self._reg = XCreateRegion()

    def reset(self):
        pass

    def update(self):
        if self._reg is None:
            raise ValueError("setup() needs to be called before update()")
        if self.dirty:
            if self.dirty < 0:
                self.dirty = 0
                XShapeCombineRegion(self._display, self._window, ShapeBounding, 0, 0, self._reg, ShapeUnion)
                self._reg = XCreateRegion()
            for r in self.invis_rects[self.dirty:]:
                XUnionRectWithRegion(XRectangle(r.x, r.y, r.w, r.h), self._reg, self._reg)
            self.dirty = 0
            XShapeCombineRegion(self._display, self._window, ShapeBounding, 0, 0, self._reg, ShapeSubtract)
