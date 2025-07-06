import pygame as py
import random
import json
import os
from sprites.player import Player
from sprites.enemies import Enemy
from sprites.weapons import Weapon
from sprites.projectiles import Yoyo
from config import CONSTANTS, LEVELS_DIR

class LevelScene:
    def __init__(self, level_id):
        self.level_id = level_id
        self.players = []
        self.enemies = []
        self.weapons = []
        self.effects = []
        self.bullets = py.sprite.Group()
        self.level_data = {}
        self.load_level_data()
        self.finished = False
        self.winner_scene = None

    def load_level_data(self):
        level_file = os.path.join(LEVELS_DIR, f"{self.level_id}.json")
        with open(level_file, "r", encoding="utf-8") as f:
            self.level_data = json.load(f)

    def set_player_choices(self, p1_gender, p2_gender):
        spawn = self.level_data["player_spawn"]
        self.players = [
            Player(*spawn["player1"], p1_gender, controls='wasd', name="Игрок 1"),
            Player(*spawn["player2"], p2_gender, controls='arrows', name="Игрок 2")
        ]
        self.spawn_weapons_and_enemies()

    def spawn_weapons_and_enemies(self):
        self.weapons = []
        self.enemies = []
        num_weapons = random.randint(3, 8)
        placed_positions = []

        screen_width, screen_height = self.level_data["world_size"]

        for _ in range(num_weapons):
            attempts = 0
            while attempts < 100:
                x = random.randint(32, screen_width - 32)
                y = random.randint(32, screen_height - 32)
                new_rect = py.Rect(x, y, 32, 32)

                if all(not new_rect.colliderect(py.Rect(px, py_, 32, 32).inflate(100, 100)) for px, py_ in
                       placed_positions) and \
                        all(not new_rect.colliderect(p.rect.inflate(100, 100)) for p in self.players):

                    placed_positions.append((x, y))
                    available_weapons = [w for w in CONSTANTS["weapons"]["types"] if w != "fist"]
                    weapon_type = random.choice(available_weapons)
                    weapon = Weapon(x, y, weapon_type=weapon_type)
                    self.weapons.append(weapon)

                    for _ in range(random.randint(1, 3)):
                        offset_x = random.randint(-80, 80)
                        offset_y = random.randint(-80, 80)
                        enemy_x = max(0, min(screen_width - 40, x + offset_x))
                        enemy_y = max(0, min(screen_height - 40, y + offset_y))
                        enemy = Enemy(self.weapons, self.players, pos=(enemy_x, enemy_y))
                        self.enemies.append(enemy)
                    break
                attempts += 1

    def handle_event(self, event):
        if event.type == py.KEYDOWN:
            if event.key == py.K_SPACE:
                self.players[0].attack(self.enemies + self.players[1:], self.bullets, self.effects)
            elif event.key == py.K_KP_PLUS:
                self.players[1].attack(self.enemies + self.players[:1], self.bullets, self.effects)
            elif event.key == py.K_q:
                self.players[0].switch_weapon(-1)
            elif event.key == py.K_e:
                self.players[0].switch_weapon(1)
            elif event.key == py.K_KP7:
                self.players[1].switch_weapon(-1)
            elif event.key == py.K_KP8:
                self.players[1].switch_weapon(1)

    def update(self):
        for player in self.players:
            player.handle_keys()
            player.pickup_weapon(self.weapons)
            player.update()

        for enemy in self.enemies:
            enemy.update(self.players)

        self.bullets.update()
        for bullet in self.bullets:
            if hasattr(bullet, "check_collision"):
                bullet.check_collision(self.enemies + self.players)

        for eff in self.effects[:]:
            self.effects = [eff for eff in self.effects if not isinstance(eff, Yoyo) or eff.alive()]
            eff.update(self.enemies + self.players)
            if eff.state == 'finished':
                self.effects.remove(eff)

        self.enemies = [e for e in self.enemies if e.health > 0]

    def render(self, screen):
        bg_color = tuple(self.level_data.get("background_color", (40, 40, 40)))
        screen.fill(bg_color)

        for enemy in self.enemies:
            enemy.draw(screen)

        for weapon in self.weapons:
            screen.blit(weapon.image, weapon.rect)

        for player in self.players:
            player.draw(screen)

        for bullet in self.bullets:
            if isinstance(bullet, Yoyo):
                self.bullets.draw(screen)
            else:
                screen.blit(bullet.image, bullet.rect)

        for eff in self.effects[:]:
            eff.update(self.enemies + self.players)
            if hasattr(eff, 'draw'):
                eff.draw(screen)
            if getattr(eff, 'state', None) == 'finished':
                self.effects.remove(eff)

