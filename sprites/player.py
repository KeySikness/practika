import pygame as py
from config import CONSTANTS
from sprites.weapons import Weapon

class Player:
    def __init__(self, x, y, gender, controls='wasd', name=""):
        stats = CONSTANTS["player_stats"][gender]
        self.speed = stats["speed"]
        self.health = stats["health"]
        self.gender = gender
        self.controls = controls
        self.name = name
        self.rect = py.Rect(x, y, 40, 40)
        self.facing_angle = 0
        self.inventory_limit = stats["inventory_limit"]

        self.dx = 0
        self.dy = 0

        self.weapon = Weapon(x, y, "fist")
        self.inventory = [Weapon(self.rect.x, self.rect.y, "fist")]
        self.current_weapon_index = 0
        self.active_boomerang = None
        self.active_yoyo = None
        self.stunned = False
        self.stun_end_time = 0
        self.weapon_in_use = False
        self.last_dropped_weapon_time = 0
        self.drop_cooldown_ms = 800

        self.sprite_sheet = py.image.load(stats["image"]).convert_alpha()
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.frames = self.load_frames(self.sprite_sheet)
        self.frames = [py.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2)) for frame in
                       self.frames]

    def pickup_weapon(self, weapons):
        now = py.time.get_ticks()
        for weapon in weapons[:]:
            if self.rect.colliderect(weapon.rect):
                if now - self.last_dropped_weapon_time < self.drop_cooldown_ms:
                    continue

                if len(self.inventory) < self.inventory_limit:
                    weapons.remove(weapon)

                    if len(self.inventory) == 1 and self.inventory[0].weapon_type == "fist":
                        self.inventory.pop(0)

                    self.inventory.append(weapon)
                    self.current_weapon_index = len(self.inventory) - 1
                    self.weapon = self.inventory[self.current_weapon_index]

    def switch_weapon(self, direction):
        if not self.inventory:
            return
        self.current_weapon_index = (self.current_weapon_index + direction) % len(self.inventory)
        self.weapon = self.inventory[self.current_weapon_index]

    def update(self):
        self.weapon = self.get_current_weapon()
        if self.stunned:
            now = py.time.get_ticks()
            if now >= self.stun_end_time:
                self.stunned = False

        if self.dx != 0 or self.dy != 0:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
        else:
            self.current_frame = 0

        if self.weapon:
            self.weapon.rect.center = self.rect.center
            self.weapon.update()

    def attack(self, targets, bullets_group, effects_list=None):
        if self.stunned:
            return

        if self.weapon:
            self.weapon.attack(self, targets, bullets_group, effects_list)

    def get_current_weapon(self):
        if self.inventory:
            return self.inventory[self.current_weapon_index]
        return None

    def handle_keys(self):
        if getattr(self, "stunned", False):
            return

        keys = py.key.get_pressed()
        dx = dy = 0

        if self.controls == 'wasd':
            if keys[py.K_w]: dy = -self.speed
            if keys[py.K_s]: dy = self.speed
            if keys[py.K_a]: dx = -self.speed
            if keys[py.K_d]: dx = self.speed
        elif self.controls == 'arrows':
            if keys[py.K_UP]: dy = -self.speed
            if keys[py.K_DOWN]: dy = self.speed
            if keys[py.K_LEFT]: dx = -self.speed
            if keys[py.K_RIGHT]: dx = self.speed

        self.dx = dx
        self.dy = dy

        if dx != 0 or dy != 0:
            direction = py.Vector2(dx, -dy)
            self.facing_angle = direction.angle_to(py.Vector2(1, 0))

    def draw(self, surface):
        frame = self.frames[self.current_frame]
        rotated_frame = py.transform.rotate(frame, -self.facing_angle)
        frame_rect = rotated_frame.get_rect(center=self.rect.center)
        surface.blit(rotated_frame, frame_rect.topleft)

        font = py.font.SysFont(None, 20)
        name_text = font.render(f"{self.name} - HP: {self.health}", True, (255, 255, 255))
        surface.blit(name_text, (self.rect.x, self.rect.y - 30))

        weapon_name = "Без оружия"
        if self.weapon:
            weapon_data = CONSTANTS["weapons"]["stats"].get(self.weapon.weapon_type)
            if weapon_data:
                weapon_name = weapon_data.get("name", self.weapon.weapon_type)

        weapon_text = font.render(weapon_name, True, (255, 255, 0))
        surface.blit(weapon_text, (self.rect.x, self.rect.y - 15))

        weapon = self.get_current_weapon()
        if weapon:
            weapon_image = weapon.image
            rotated_image = py.transform.rotate(weapon_image, -self.facing_angle)
            weapon_rect = rotated_image.get_rect(center=self.rect.center)
            surface.blit(rotated_image, weapon_rect.topleft)

    def drop_weapon(self, weapons_on_map):
        weapon = self.get_current_weapon()
        if not weapon or weapon.weapon_type == "fist":
            return

        dropped_weapon = Weapon(self.rect.centerx, self.rect.centery, weapon.weapon_type)
        weapons_on_map.append(dropped_weapon)
        self.inventory.pop(self.current_weapon_index)

        if self.inventory:
            self.current_weapon_index %= len(self.inventory)
        else:
            self.inventory.append(Weapon(self.rect.x, self.rect.y, "fist"))
            self.current_weapon_index = 0

        self.weapon = self.inventory[self.current_weapon_index]
        self.last_dropped_weapon_time = py.time.get_ticks()

    def load_frames(self, sheet, frame_width=24, frame_height=24):
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        for i in range(sheet_width // frame_width):
            rect = py.Rect(i * frame_width, 0, frame_width, frame_height)
            frames.append(sheet.subsurface(rect))
        return frames