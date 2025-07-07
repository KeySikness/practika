import pygame as pg

DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
BG_COLOR = (30, 30, 30)
SELECTED_COLOR = (255, 215, 0)
#ITEM_COLOR = (100, 100, 255)

INVENTORY_SLOTS = 10
SLOT_SIZE = 60
SLOT_MARGIN = 10
INVENTORY_HEIGHT = SLOT_SIZE + SLOT_MARGIN * 2

class Inventory:
    def __init__(self, screen_width, screen_height):
        self.slots = [None for _ in range(INVENTORY_SLOTS)]
        self.selected_index = None
        self.rect = pg.Rect(
            (screen_width - (SLOT_SIZE * INVENTORY_SLOTS + SLOT_MARGIN * (INVENTORY_SLOTS - 1))) // 2,
            screen_height - INVENTORY_HEIGHT,
            SLOT_SIZE * INVENTORY_SLOTS + SLOT_MARGIN * (INVENTORY_SLOTS - 1),
            INVENTORY_HEIGHT,
        )

        self.slot_rects = []
        for i in range(INVENTORY_SLOTS):
            slot_x = self.rect.x + i * (SLOT_SIZE + SLOT_MARGIN)
            slot_y = self.rect.y + SLOT_MARGIN
            self.slot_rects.append(pg.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE))

        self.item_images = {
            "bat": pg.image.load("assets/бита.png").convert_alpha(),
            "rope": pg.image.load("assets/веревка.png").convert_alpha(),
            "nail gun": pg.image.load("assets/гвоздомет.png").convert_alpha(),
            "stick": pg.image.load("assets/клюшка.png").convert_alpha(),
            "hammer": pg.image.load("assets/молоток.png").convert_alpha(),
            "knife_1": pg.image.load("assets/нож 1.png").convert_alpha(),
            "knife_2": pg.image.load("assets/нож 2.png").convert_alpha(),
            "pan": pg.image.load("assets/сковорода.png").convert_alpha(),
            "axe": pg.image.load("assets/топор.png").convert_alpha(),
        }
        self.selected_item_name = " "

    def draw(self, screen):
        for i in range(INVENTORY_SLOTS):
            rect = self.slot_rects[i]
            pg.draw.rect(screen, DARK_GRAY, rect)
            border_color = LIGHT_GRAY
            border_width = 2
            if i == self.selected_index:
                border_color = SELECTED_COLOR
                border_width = 4
            pg.draw.rect(screen, border_color, rect, border_width)

            item = self.slots[i]
            if item:
                if item in self.item_images:
                    image = self.item_images[item]
                    image_rect = image.get_rect(center=rect.center)
                    screen.blit(image, image_rect)
                else:
                    print(f"No image found for item: {item}")

        if self.selected_index is not None:
            selected_item = self.slots[self.selected_index]
            if selected_item:
                self.selected_item_name = selected_item
                font = pg.font.Font(None, 36)
                text_surface = font.render(self.selected_item_name, True, (255, 255, 255))
                screen.blit(text_surface, (40, 27))

    def add_item(self, item):
        if None in self.slots:
            for i in range(INVENTORY_SLOTS):
                if self.slots[i] is None:
                    self.slots[i] = item
                    return True
        return False

    def select_slot_at_pos(self, pos):
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(pos):
                if self.slots[i]:
                    self.selected_index = i
                else:
                    self.selected_index = None
                return

    def use_selected_item(self):
        if self.selected_index is not None:
            item = self.slots[self.selected_index]
            if item:
                print(f"Used item in slot {self.selected_index + 1}")
                return True
        return False