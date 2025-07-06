import pygame as py
from scene_manager import SceneManager

class Button:
    def __init__(self, rect, text, callback):
        self.rect = py.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = py.font.SysFont(None, 36)
        self.hover = False

    def draw(self, surface):
        color = (180, 180, 180) if self.hover else (120, 120, 120)
        py.draw.rect(surface, color, self.rect)
        py.draw.rect(surface, (255, 255, 255), self.rect, 2)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(
            text_surf,
            (
                self.rect.x + self.rect.w // 2 - text_surf.get_width() // 2,
                self.rect.y + self.rect.h // 2 - text_surf.get_height() // 2,
            ),
        )

    def handle_event(self, event):
        if event.type == py.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == py.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()


class CharacterSelect:
    def __init__(self, default_next="level1"):
        self.font = py.font.SysFont(None, 40)
        self.player1_choice = None
        self.player2_choice = None
        self.current_player = 1
        self.next_level_id = default_next
        self.buttons = []
        self.make_buttons()

    def make_buttons(self):
        self.buttons = []
        w, h = 200, 60
        spacing = 30
        start_x = 300
        start_y = 200

        def make_button(text, gender):
            return Button(
                (start_x, start_y + len(self.buttons) * (h + spacing), w, h),
                text,
                lambda g=gender: self.select(g),
            )

        self.buttons.append(make_button("женщина", "woman"))
        self.buttons.append(make_button("мужчина", "man"))

    def select(self, gender):
        if self.current_player == 1:
            self.player1_choice = gender
            self.current_player = 2
        elif self.current_player == 2:
            self.player2_choice = gender
            self.load_level()

    def load_level(self):
        scene = SceneManager.get_instance().scenes[self.next_level_id]
        scene.set_player_choices(self.player1_choice, self.player2_choice)
        SceneManager.get_instance().set_scene(self.next_level_id)

    def on_enter(self):
        self.player1_choice = None
        self.player2_choice = None
        self.current_player = 1
        self.make_buttons()

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self):
        pass

    def render(self, screen):
        screen.fill((30, 30, 30))
        prompt = f"Игрок {self.current_player}, выбери своего бойца:"
        text = self.font.render(prompt, True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 100))
        for button in self.buttons:
            button.draw(screen)