import pygame
import sys

def run_introduction(screen):
    sc_w, sc_h = 1600, 900

    dialogues = [
        "*неистовый, прерывистый смех*",
        "Ну что, мои дороги крысы, вам нравится ваш новый домик?",
        "*смеется*",
        "Удивительное существо этот человек",
        "Стоит поставить вас в экстремальные условия и вы будете рвать и резать друг друга лишь бы выжить",
        "Ничего нового на этот раз",
        "На другом конце бункера твой враг",
        "Тебе нужно убить его. Любым способом",
        "Из этого места выберется лишь один",
        "Советую поискать хоть какое-нибудь оружие, иначе кому-то придется зубами прогрызать себе путь к выходу",
        "Давайте сразу проясним: тянуть время - плохая идея. Договариваться с соперником тоже",
        "В ваши жопы вшиты бомбы. Так что если вздумаете играть не по правилам - я подорву ваши пердаки",
        "*заливается хохотом*",
        "Я слышу все. И вижу все",
        "Да начнется представление!",
        "*карикатурный злобный смех*"
    ]
    current_dialogue_index = 0
    font = pygame.font.Font(None, 36)
    text_color = (255, 255, 255)
    dialogue_box_color = (50, 50, 50)
    dialogue_box_height = 150

    def draw_dialogue(text):
        dialogue_box = pygame.Surface((sc_w, dialogue_box_height))
        dialogue_box.fill(dialogue_box_color)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(sc_w // 2, dialogue_box_height // 2))
        dialogue_box.blit(text_surface, text_rect)
        screen.blit(dialogue_box, (0, sc_h - dialogue_box_height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_dialogue_index + 1 >= len(dialogues):
                        running = False
                    else:
                        current_dialogue_index += 1

        screen.fill((0, 0, 0))
        draw_dialogue(dialogues[current_dialogue_index])
        pygame.display.flip()

    return True