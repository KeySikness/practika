import pygame as py
import os
import random
from config import CONSTANTS

ENEMY_CONFIG = CONSTANTS["enemy"]

class Enemy(py.sprite.Sprite):
    enemy_images = []

    @classmethod
    def load_images(cls):
        if cls.enemy_images:
            return

        enemy_folder = os.path.join("assets", "images", "enemies")
        if os.path.exists(enemy_folder):
            for filename in sorted(os.listdir(enemy_folder))[:3]:
                path = os.path.join(enemy_folder, filename)
                try:
                    image = py.image.load(path).convert_alpha()
                    image = py.transform.scale(image, (ENEMY_CONFIG["size"], ENEMY_CONFIG["size"]))
                    cls.enemy_images.append(image)
                except Exception as e:
                    print(f"Ошибка загрузки {filename}: {e}")

        if not cls.enemy_images:
            default_image = py.Surface((ENEMY_CONFIG["size"], ENEMY_CONFIG["size"]))
            default_image.fill((100, 100, 100))
            cls.enemy_images.append(default_image)

    def __init__(self, weapons, players, pos=None):
        super().__init__()
        Enemy.load_images()
        self.image = random.choice(Enemy.enemy_images)
        self.rect = self.image.get_rect()

        if pos is not None:
            self.rect.center = pos
        else:
            self.spawn_near_weapon(weapons, players)

        self.speed = ENEMY_CONFIG["speed"]
        health_min, health_max = ENEMY_CONFIG["health_range"]
        self.health = random.randint(health_min, health_max)
        self.damage = ENEMY_CONFIG["damage"]
        self.attack_delay = ENEMY_CONFIG["attack_delay"]
        self.last_attack_time = py.time.get_ticks()
        self.stunned = False
        self.stun_end_time = 0

    def spawn_near_weapon(self, weapons, players):
        min_dist = ENEMY_CONFIG["min_spawn_distance"]
        max_attempts = 20
        attempts = 0

        while attempts < max_attempts:
            if not weapons:
                self.rect.topleft = (random.randint(100, 700), random.randint(100, 500))
                return

            weapon = random.choice(weapons)
            wx, wy = weapon.rect.center
            offset_x = random.randint(-100, 100)
            offset_y = random.randint(-100, 100)
            self.rect.center = (wx + offset_x, wy + offset_y)

            too_close = any(
                (self.rect.centerx - p.rect.centerx)**2 + (self.rect.centery - p.rect.centery)**2 < min_dist**2
                for p in players
            )
            if not too_close:
                return
            attempts += 1

        self.rect.topleft = (random.randint(100, 700), random.randint(100, 500))

    def update(self, players):
        now = py.time.get_ticks()
        if self.stunned and now >= self.stun_end_time:
            self.stunned = False

        if self.stunned:
            return

        if not players:
            return

        closest_player = min(
            players,
            key=lambda p: (p.rect.centerx - self.rect.centerx)**2 + (p.rect.centery - self.rect.centery)**2
        )

        dx = closest_player.rect.centerx - self.rect.centerx
        dy = closest_player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2) ** 0.5

        if distance != 0:
            dx /= distance
            dy /= distance
            self.rect.move_ip(dx * self.speed, dy * self.speed)

        now = py.time.get_ticks()
        if self.rect.colliderect(closest_player.rect) and now - self.last_attack_time > self.attack_delay:
            closest_player.health -= self.damage
            self.last_attack_time = now


    def draw(self, surface):
        surface.blit(self.image, self.rect)