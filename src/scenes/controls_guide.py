import pygame as py
from src.scenes.menu import Button
from scene_manager import SceneManager

class ControlsInfoScene:
    def __init__(self, next_scene):
        self.next_scene = next_scene
        self.window_size = (1600, 900)
        self.button = None
        self.font = py.font.SysFont("Comic Sans MS", 32)
        self.title_font = py.font.SysFont("Comic Sans MS", 48, bold=True)
        self.bg_color = (30, 30, 30)

    def on_enter(self):
        self.update_layout(self.window_size)

    def update_layout(self, window_size):
        self.window_size = window_size
        w, h = window_size
        self.button = Button("Далее", (w // 2 - 150, h - 120), (300, 80))

    def handle_event(self, event):
        if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = py.mouse.get_pos()
            if self.button.is_hovered(mouse_pos):
                SceneManager.get_instance().set_scene("character_select")

    def update(self):
        mouse_pos = py.mouse.get_pos()
        self.button.update(mouse_pos)

    def render(self, screen):
        screen.fill(self.bg_color)

        player1_title = self.title_font.render("Игрок 1:", True, (255, 255, 255))
        player2_title = self.title_font.render("Игрок 2:", True, (255, 255, 255))
        screen.blit(player1_title, (100, 100))
        screen.blit(player2_title, (self.window_size[0] // 2 + 100, 100))

        controls1 = [
            "WASD - передвижение",
            "Q / E - смена оружия",
            "Пробел - атака",
            "R - выбросить оружие"
        ]
        for i, text in enumerate(controls1):
            line = self.font.render(text, True, (220, 220, 220))
            screen.blit(line, (100, 160 + i * 50))

        controls2 = [
            "Стрелки - передвижение",
            "NUM7 / NUM8 - смена оружия",
            "Enter - атака",
            "Правый Ctrl - выбросить оружие"
        ]
        for i, text in enumerate(controls2):
            line = self.font.render(text, True, (220, 220, 220))
            screen.blit(line, (self.window_size[0] // 2 + 100, 160 + i * 50))

        # Кнопка
        self.button.draw(screen)
