import pygame
from scene_manager import SceneManager
from audio_manager import AudioManager

class IntroductionScene:
    def __init__(self, next_scene="character_select"):
        self.dialogues = [
            "*неистовый, прерывистый смех*",
            "Ну что, мои дороги крысы, вам нравится ваш новый домик?",
            "*смеется*",
            "Удивительное существо этот человек",
            "Стоит поставить вас в экстремальные условия и вы будете рвать и резать друг друга лишь бы выжить",
            "Ничего нового на этот раз",
            "На другом конце бункера твой враг",
            "Тебе нужно убить его. Любым способом",
            "Из этого места выберется лишь один",
            "Советую поискать хоть какое-нибудь оружие...",
            "В ваши жопы вшиты бомбы. Так что если вздумаете играть не по правилам - я подорву ваши пердаки",
            "*заливается хохотом*",
            "Я слышу все. И вижу все",
            "Да начнется представление!",
            "*карикатурный злобный смех*"
        ]
        self.index = 0
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0)
        self.box_color = (50, 50, 50)
        self.box_height = 150
        self.next_scene = next_scene
        self.window_size = (1600, 900)
        self.skip_hint_font = pygame.font.SysFont("Comic Sans MS", 24, bold=True)
        self.skip_hint_text = self.skip_hint_font.render("Чтобы пропустить нажмите ESC", True, (255, 255, 255))
        self.space_hint_text = self.skip_hint_font.render("Чтобы продолжить нажмите SPACE", True, (255, 255, 255))

    def on_enter(self):
        self.index = 0
        AudioManager.get_instance().play_music(AudioManager.get_instance().tracks["ambient"])

    def update_layout(self, window_size):
        self.window_size = window_size

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.index += 1
            if self.index >= len(self.dialogues):
                SceneManager.get_instance().set_scene(self.next_scene)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            SceneManager.get_instance().set_scene(self.next_scene)

    def update(self):
        pass

    def render(self, screen):
        screen.fill(self.bg_color)
        screen.blit(self.skip_hint_text, (20, 20))
        screen.blit(self.space_hint_text, (20, 50))

        w, h = self.window_size
        dialogue_box = pygame.Surface((w, self.box_height))
        dialogue_box.fill(self.box_color)

        if self.index < len(self.dialogues):
            text = self.dialogues[self.index]
            text_surface = self.font.render(text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(w // 2, self.box_height // 2))
            dialogue_box.blit(text_surface, text_rect)

        screen.blit(dialogue_box, (0, h - self.box_height))
