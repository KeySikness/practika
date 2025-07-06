import pygame as py
from config import CONSTANTS

class VictoryScene:
    def __init__(self, winner_name):
        self.winner_name = winner_name
        self.font = py.font.SysFont(None, 64)
        self.small_font = py.font.SysFont(None, 36)
        self.finished = False

    def handle_event(self, event):
        if event.type == py.KEYDOWN and event.key == py.K_RETURN:
            self.finished = True

    def update(self):
        pass

    def render(self, screen):
        screen.fill((0, 0, 0))
        text = f"{self.winner_name} победил!"
        text_surf = self.font.render(text, True, (255, 255, 255))
        sub_surf = self.small_font.render("Нажмите ENTER, чтобы продолжить", True, (200, 200, 200))

        screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, 250))
        screen.blit(sub_surf, (screen.get_width() // 2 - sub_surf.get_width() // 2, 320))