import pygame
import pygame as pg
import sys

WIDTH, HEIGHT = 1600, 900
BUTTON_COLOR = (108, 45, 45)
BUTTON_HOVER_COLOR = (130, 52, 52)
TEXT_COLOR = (0, 0, 0)

FONT = pg.font.SysFont("Comic Sans MS", 48)
background_image = pygame.transform.scale(pygame.image.load("assets/FINISH.jpg"), (WIDTH, HEIGHT))

class Button:
    def __init__(self, text, pos, size):
        self.text = text
        self.pos = pos
        self.size = size
        self.rect = pg.Rect(pos, size)
        self.color = BUTTON_COLOR
        self.text_surf = FONT.render(text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect, border_radius=8)
        surface.blit(self.text_surf, self.text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def final_screen(screen, screen_width, screen_height, message):
    pg.init()
    text = FONT.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))

    menu_button = Button("Меню", (screen_width // 2 - 150, screen_height // 2 - 20), (300, 80))
    exit_button = Button("Выход", (screen_width // 2 - 150, screen_height // 2 + 80), (300, 80))

    running = True
    last_hovered_button = None

    while running:
        mouse_pos = pg.mouse.get_pos()

        screen.blit(background_image, (0, 0))
        screen.blit(text, text_rect)

        for button in [menu_button, exit_button]:
            if button.is_hovered(mouse_pos):
                button.color = BUTTON_HOVER_COLOR
                if last_hovered_button != button:
                    last_hovered_button = button
            else:
                button.color = BUTTON_COLOR
            button.draw(screen)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if menu_button.is_hovered(mouse_pos):
                    return "Menu"
                elif exit_button.is_hovered(mouse_pos):
                    pg.quit()
                    sys.exit()

        pg.display.flip()
    return "Menu"
window = pygame.display.set_mode((WIDTH, HEIGHT))