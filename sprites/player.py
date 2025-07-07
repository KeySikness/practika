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
        self.color = tuple(stats["color"])
        self.rect = py.Rect(x, y, 40, 40)
        self.facing_angle = 0
        self.weapon = Weapon(x, y, "fist")
        self.inventory = [Weapon(self.rect.x, self.rect.y, "fist")]
        self.current_weapon_index = 0
        self.inventory_limit = stats["inventory_limit"]
        self.active_boomerang = None
        self.active_yoyo = None
        self.stunned = False
        self.stun_end_time = 0
        self.weapon_in_use = False
        self.last_dropped_weapon_time = 0
        self.drop_cooldown_ms = 500

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

        if dx != 0 or dy != 0:
            self.facing_angle = py.Vector2(dx, dy).angle_to(py.Vector2(1, 0))

        self.rect.move_ip(dx, dy)

    def draw(self, surface):
        py.draw.rect(surface, self.color, self.rect)

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

    def draw_scaled(self, surface, scale_func):
        scaled_pos = scale_func(self.rect.topleft)
        scaled_size = (
            int(self.rect.width * scale_func((1, 0))[0]),
            int(self.rect.height * scale_func((0, 1))[1])
        )
        scaled_rect = py.Rect(scaled_pos, scaled_size)

        py.draw.rect(surface, self.color, scaled_rect)

        font = py.font.SysFont(None, 20)
        name_text = font.render(f"{self.name} - HP: {self.health}", True, (255, 255, 255))
        surface.blit(name_text, (scaled_rect.x, scaled_rect.y - 30))

        weapon_name = "Без оружия"
        if self.weapon:
            weapon_data = CONSTANTS["weapons"]["stats"].get(self.weapon.weapon_type)
            if weapon_data:
                weapon_name = weapon_data.get("name", self.weapon.weapon_type)

        weapon_text = font.render(weapon_name, True, (255, 255, 0))
        surface.blit(weapon_text, (scaled_rect.x, scaled_rect.y - 15))

        weapon = self.get_current_weapon()
        if weapon:
            weapon_image = weapon.image
            rotated_image = py.transform.rotate(weapon_image, -self.facing_angle)

            scaled_center = (
                scaled_rect.x + scaled_rect.width // 2,
                scaled_rect.y + scaled_rect.height // 2
            )
            weapon_rect = rotated_image.get_rect(center=scaled_center)
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




