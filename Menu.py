import pygame
import sys
pygame.init()

clock = pygame.time.Clock()
WIDTH, HEIGHT = 1600, 900
BUTTON_COLOR = (108, 45, 45)
BUTTON_HOVER_COLOR = (130, 52, 52)
TEXT_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Comic Sans MS", 48)

hover_sound = pygame.mixer.Sound("assets\hover.mp3")
#background_image = pygame.transform.scale(pygame.image.load(" "), (WIDTH, HEIGHT)) # После выбора картинки для заставки

window = pygame.display.set_mode((WIDTH, HEIGHT))

class Button:
    def __init__(self, text, pos, size):
        self.text = text
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.color = BUTTON_COLOR
        self.text_surf = FONT.render(text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        surface.blit(self.text_surf, self.text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def main_menu(window):
    play_button = Button("Играть", (WIDTH // 2 - 150, HEIGHT // 2 - 60), (300, 80))
    exit_button = Button("Выход", (WIDTH // 2 - 150, HEIGHT // 2 + 60), (300, 80))
    last_hovered_button = None
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
#        window.blit(background_image, (0, 0))    # После выбора картинки для заставки, заменить на это

        for button in [play_button, exit_button]:
            if button.is_hovered(mouse_pos):
                button.color = BUTTON_HOVER_COLOR
                if last_hovered_button != button:
                    hover_sound.play()
                    last_hovered_button = button
            else:
                button.color = BUTTON_COLOR
            button.draw(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.is_hovered(mouse_pos):
                    return "Introduction"
                elif exit_button.is_hovered(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)