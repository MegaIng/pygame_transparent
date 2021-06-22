from typing import Tuple

import pygame as pg

__version__ = "0.0.1"

from pygame_transparent.trans_base import Transparent


def transparent(screen: pg.Surface, invis_color: Tuple[int, int, int] = (1, 0, 0)) -> Transparent:
    driver = pg.display.get_driver()
    if driver == "x11":
        from .trans_x11 import X11Transparent
        return X11Transparent(screen, invis_color)
    elif driver == "windows":
        from .trans_windows import WindowsTransparent
        return WindowsTransparent(screen, invis_color)
    else:
        raise NotImplementedError(f"Unsupported Video Driver {driver!r}")
