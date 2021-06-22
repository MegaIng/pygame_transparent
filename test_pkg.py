import pygame as pg
from pygame_transparent import transparent

pg.init()

W, H = 640, 480
FLAGS = 0

screen = pg.display.set_mode((W, H), FLAGS)
W, H = screen.get_size()
trans = transparent(screen)
trans.setup()

clock = pg.time.Clock()
running = True
start = None
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False
        elif event.type == pg.VIDEORESIZE:
            screen = pg.display.set_mode(event.size, FLAGS)
            W, H = screen.get_size()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            start = event.pos
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            r = pg.Rect(start, (event.pos[0]-start[0],event.pos[1]-start[1]))
            trans.add(r)
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            trans.clear()
    # Logic
    dt = clock.tick()

    # Render
    screen.fill((0, 0, 0))

    trans.update()
    pg.display.update()
    pg.display.set_caption(f"FPS: {clock.get_fps():.2f}")
