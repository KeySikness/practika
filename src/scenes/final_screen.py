import pygame
from src.scenes.menu import Button
from scene_manager import SceneManager

class WinScene:
    def __init__(self, winner_index, level_scene_name="level", menu_scene_name="main_menu"):
        self.winner_index = winner_index
        self.level_scene_name = level_scene_name
        self.menu_scene_name = menu_scene_name
        self.retry_button = None
        self.menu_button = None
        self.window_size = (1600, 900)

    def on_enter(self):
        self.update_layout(self.window_size)

    def update_layout(self, window_size):
        self.window_size = window_size
        w, h = window_size
        self.retry_button = Button("Заново", (w // 2 - 150, h // 2 + 40), (300, 80))
        self.menu_button = Button("Меню", (w // 2 - 150, h // 2 + 140), (300, 80))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.retry_button.is_hovered(mouse_pos):
                manager = SceneManager.get_instance()
                level_scene = manager.scenes.get(self.level_scene_name)
                if level_scene:
                    level_scene.restart_level()
                    manager.set_scene(self.level_scene_name)
            elif self.menu_button.is_hovered(mouse_pos):
                SceneManager.get_instance().set_scene(self.menu_scene_name)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.retry_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)

    def render(self, screen):
        screen.fill((30, 30, 30))

        font = pygame.font.SysFont("Comic Sans MS", 64)
        win_text = font.render(f"Игрок {self.winner_index + 1} выжил... остался только один", True, (255, 255, 255))
        text_rect = win_text.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 2 - 100))
        screen.blit(win_text, text_rect)

        self.retry_button.draw(screen)
        self.menu_button.draw(screen)
