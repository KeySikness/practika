import pygame
import sys
from audio_manager import AudioManager
pygame.init()

clock = pygame.time.Clock()
WIDTH, HEIGHT = 1600, 900
BUTTON_COLOR = (108, 45, 45)
BUTTON_HOVER_COLOR = (130, 52, 52)
TEXT_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Comic Sans MS", 48)

# background_image = pygame.transform.scale(pygame.image.load(" "), (WIDTH, HEIGHT)) # После выбора картинки для заставки

window = pygame.display.set_mode((WIDTH, HEIGHT))

class Button:
    def __init__(self, text, pos, size):
        self.text = text
        self.size = size
        self.color = BUTTON_COLOR
        self.text_surf = FONT.render(text, True, TEXT_COLOR)
        self.set_position(pos)

    def set_position(self, pos):
        self.pos = pos
        self.rect = pygame.Rect(pos, self.size)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        surface.blit(self.text_surf, self.text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        self.color = BUTTON_HOVER_COLOR if self.is_hovered(mouse_pos) else BUTTON_COLOR




class MainMenuScene:
    def __init__(self, next_scene):
        self.next_scene = next_scene
        self.play_button = None
        self.exit_button = None
        self.window_size = (1600, 900)

    def on_enter(self):
        self.update_layout(self.window_size)
        AudioManager.get_instance().play_music(AudioManager.get_instance().tracks["menu"])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.play_button.is_hovered(mouse_pos):
                from scene_manager import SceneManager
                SceneManager.get_instance().set_scene(self.next_scene)
            elif self.exit_button.is_hovered(mouse_pos):
                pygame.quit()
                sys.exit()

    def update_layout(self, window_size):
        self.window_size = window_size
        w, h = window_size
        self.play_button = Button("Играть", (w // 2 - 150, h // 2 - 60), (300, 80))
        self.exit_button = Button("Выход", (w // 2 - 150, h // 2 + 60), (300, 80))

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in [self.play_button, self.exit_button]:
            if button.is_hovered(mouse_pos):
                button.color = BUTTON_HOVER_COLOR
                self.last_hovered = button
            else:
                button.color = BUTTON_COLOR

    def render(self, screen):
        screen.fill((30, 30, 30))
        self.play_button.draw(screen)
        self.exit_button.draw(screen)