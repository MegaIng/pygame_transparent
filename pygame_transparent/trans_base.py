from abc import abstractmethod, ABC
from typing import Tuple

import pygame as pg


class Transparent(ABC):
    def __init__(self, screen: pg.Surface, invis_color: Tuple[int, int, int] = (1, 0, 0)):
        self.screen = screen
        self.invis_color = invis_color
        self.invis_rects = []
        self.dirty = -1
        self.removed = []

    def add(self, *rects: pg.Rect):
        self.invis_rects.extend(rects)
        if not self.dirty and rects:
            self.dirty = len(self.invis_rects) - len(rects) or -1

    def remove(self, *rects: pg.Rect):
        for r in rects:
            self.invis_rects.remove(r)
        self.dirty = -1

    def clear(self):
        self.invis_rects = []
        self.dirty = -1

    @abstractmethod
    def setup(self):
        """
        Initially setups the required changes to make the window transparent.
        Needs to be called once before any call to update, and after reset has been called.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Tries to brings everything back to normal. Might not succeed.
        The only safe way to do that is to call `set_mode` again.
        """
        pass

    @abstractmethod
    def update(self):
        """
        Copies the current internal state to the screen. Needs to be called everything a rect is
        added/removed.
        """
        pass
