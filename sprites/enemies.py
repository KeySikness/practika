import pygame as py
import random
import math
from config import CONSTANTS

ENEMY_CONFIG = CONSTANTS["enemy"]

class Enemy(py.sprite.Sprite):
    enemy_images = []

    @classmethod
    def load_images(cls):
        if cls.enemy_images:
            return
        sheet_path = ENEMY_CONFIG["image"]
        sheet = py.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = ENEMY_CONFIG["size"]
        frame_height = sheet_height
        num_frames = sheet_width // frame_width
        cls.enemy_images = [
            sheet.subsurface(py.Rect(i * frame_width, 0, frame_width, frame_height))
            for i in range(num_frames)
        ]

    def __init__(self, weapons, players, existing_enemies=None, pos=None):
        super().__init__()
        Enemy.load_images()
        self.image = random.choice(Enemy.enemy_images)
        self.rect = self.image.get_rect()

        if pos is not None:
            self.rect.center = pos
        else:
            self.spawn_near_weapon(weapons, players, existing_enemies or [])

        self.speed = ENEMY_CONFIG["speed"]
        health_min, health_max = ENEMY_CONFIG["health_range"]
        self.health = random.randint(health_min, health_max)
        self.damage = ENEMY_CONFIG["damage"]
        self.attack_delay = ENEMY_CONFIG["attack_delay"]
        self.last_attack_time = py.time.get_ticks()
        self.stunned = False
        self.stun_end_time = 0

        self.last_known_position = None
        self.last_seen_time = 0
        self.memory_duration = 15000

        self.last_animation_time = py.time.get_ticks()
        self.current_frame = 0
        self.animation_speed = 200
        self.image = Enemy.enemy_images[self.current_frame]
        self.facing_right = True

    def spawn_near_weapon(self, weapons, players, other_enemies):
        min_dist = ENEMY_CONFIG["min_spawn_distance"]
        max_attempts = 30
        attempts = 0

        while attempts < max_attempts:
            if not weapons:
                self.rect.topleft = (random.randint(100, 700), random.randint(100, 500))
            else:
                weapon = random.choice(weapons)
                wx, wy = weapon.rect.center
                offset_x = random.randint(-100, 100)
                offset_y = random.randint(-100, 100)
                self.rect.center = (wx + offset_x, wy + offset_y)

            too_close_to_players = any(
                (self.rect.centerx - p.rect.centerx) ** 2 + (self.rect.centery - p.rect.centery) ** 2 < min_dist ** 2
                for p in players
            )
            overlaps_other_enemies = any(self.rect.colliderect(e.rect.inflate(-10, -10)) for e in other_enemies)

            if not too_close_to_players and not overlaps_other_enemies:
                return

            attempts += 1
        self.rect.topleft = (random.randint(100, 700), random.randint(100, 500))

    def update(self, players, world_size, game_map=None):
        now = py.time.get_ticks()
        if self.stunned and now >= self.stun_end_time:
            self.stunned = False

        if self.stunned or not players:
            return

        closest_player = min(
            players,
            key=lambda p: (p.rect.centerx - self.rect.centerx) ** 2 + (p.rect.centery - self.rect.centery) ** 2
        )

        player_pos = closest_player.rect.center
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        vision_range = 700

        can_see = False
        if distance <= vision_range and game_map and self.can_see_player(closest_player, game_map):
            can_see = True
            self.last_known_position = player_pos
            self.last_seen_time = now

        if abs(dx) > 1:
            self.facing_right = dx > 0
        # запоминаем где был
        if self.last_known_position and now - self.last_seen_time <= self.memory_duration:
            self.move_towards(self.last_known_position, game_map)
        # атака если рядом
        if can_see and self.rect.colliderect(closest_player.rect) and now - self.last_attack_time > self.attack_delay:
            closest_player.health -= self.damage
            self.last_attack_time = now

        if now - self.last_animation_time >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(Enemy.enemy_images)
            base_image = Enemy.enemy_images[self.current_frame]
            # отражение
            flipped = py.transform.flip(base_image, not self.facing_right, False)
            scale = ENEMY_CONFIG.get("scale", 1.0)
            if scale != 1.0:
                width = int(flipped.get_width() * scale)
                height = int(flipped.get_height() * scale)
                flipped = py.transform.scale(flipped, (width, height))

            self.image = flipped
            self.rect = self.image.get_rect(center=self.rect.center)
            self.last_animation_time = now

    def draw(self, surface, camera_offset):
        rel_pos = py.Vector2(self.rect.topleft) - camera_offset
        surface.blit(self.image, rel_pos)

        font = py.font.SysFont(None, 20)
        hp_text = font.render(f"HP: {self.health}", True, (255, 0, 0))
        surface.blit(hp_text, (rel_pos.x, rel_pos.y - 20))

    def draw_scaled(self, surface, scale_func):
        scaled_pos = scale_func(self.rect.topleft)
        scale_x = scale_func((1, 0))[0]
        scale_y = scale_func((0, 1))[1]
        scaled_size = (int(self.rect.width * scale_x), int(self.rect.height * scale_y))

        scaled_image = py.transform.scale(self.image, scaled_size)
        surface.blit(scaled_image, scaled_pos)

    def can_see_player(self, player, game_map):
        x0, y0 = self.rect.center
        x1, y1 = player.rect.center

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1

        if dx > dy:
            err = dx / 2.0
            while x != x1:
                if not game_map.is_walkable(int(x), int(y)):
                    return False
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                if not game_map.is_walkable(int(x), int(y)):
                    return False
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

        return True

    def is_rect_valid(self, game_map):
        points = [
            self.rect.center,
            self.rect.topleft,
            self.rect.topright,
            self.rect.bottomleft,
            self.rect.bottomright
        ]
        return all(game_map.is_walkable(int(x), int(y)) for (x, y) in points)

    def move_towards(self, target, game_map):
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        dx /= distance
        dy /= distance

        original_rect = self.rect.copy()
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        if not self.is_rect_valid(game_map):
            self.rect = original_rect
            for angle in [30, -30, 45, -45, 60, -60]:
                rad = math.radians(angle)
                new_dx = dx * math.cos(rad) - dy * math.sin(rad)
                new_dy = dx * math.sin(rad) + dy * math.cos(rad)

                self.rect.x = original_rect.x + new_dx * self.speed
                self.rect.y = original_rect.y + new_dy * self.speed
                if self.is_rect_valid(game_map):
                    break
                else:
                    self.rect = original_rect

    def load_sprite_strip(image_path, frame_width, frame_height):
        sprite_sheet = py.image.load(image_path).convert_alpha()
        sheet_width = sprite_sheet.get_width()
        frame_count = sheet_width // frame_width
        frames = []

        for i in range(frame_count):
            frame = sprite_sheet.subsurface(py.Rect(i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)

        return frames