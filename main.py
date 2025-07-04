import pygame as py
import sys
import os

def main():
    py.init()

    screen_size = (800, 600)
    screen = py.display.set_mode(screen_size, py.RESIZABLE)
    py.display.set_caption("game")

    clock = py.time.Clock()

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.VIDEORESIZE:
                screen_size = event.size
                screen = py.display.set_mode(screen_size, py.RESIZABLE)

        py.display.flip()
        clock.tick(60)

    py.quit()
    sys.exit()

if __name__ == "__main__":
    main()

#тут кароче игра лол

# 　　　　　／＞　 フ
# 　　　　　| 　_　 _|
# 　 　　　／`ミ _x 彡
# 　　 　 /　　　 　 |
# 　　　 /　 ヽ　　 ﾉ
# 　／￣|　　 |　|　|
# 　| (￣ヽ＿_ヽ_)_)
# 　＼二つ