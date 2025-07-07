import pygame as py
import random
import json
import os
from sprites.player import Player
from sprites.enemies import Enemy
from sprites.weapons import Weapon
from sprites.projectiles import MolotovEffect
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
        self.finished = False
        self.winner_scene = None

        self.window_size = (1600, 900)
        self.scale_x = 1
        self.scale_y = 1

        self.load_level_data()

    def load_level_data(self):
        level_file = os.path.join(LEVELS_DIR, f"{self.level_id}.json")
        with open(level_file, "r", encoding="utf-8") as f:
            self.level_data = json.load(f)

    def on_enter(self):
        self.finished = False

    def update_layout(self, window_size):
        self.window_size = window_size
        world_w, world_h = self.level_data["world_size"]
        self.scale_x = window_size[0] / world_w
        self.scale_y = window_size[1] / world_h

    def scale_pos(self, pos):
        x, y = pos
        return int(x * self.scale_x), int(y * self.scale_y)

    def set_player_choices(self, p1_gender, p2_gender):
        spawn = self.level_data["player_spawn"]
        self.players = [
            Player(*spawn["player1"], p1_gender, controls='wasd', name="Игрок 1"),
            Player(*spawn["player2"], p2_gender, controls='arrows', name="Игрок 2")
        ]
        self.spawn_weapons_and_enemies()

    def spawn_weapons_and_enemies(self):
        self.weapons.clear()
        self.enemies.clear()

        num_weapons = random.randint(3, 8)
        placed_positions = []

        world_w, world_h = self.level_data["world_size"]

        for _ in range(num_weapons):
            for _ in range(100):  # max attempts
                x = random.randint(32, world_w - 32)
                y = random.randint(32, world_h - 32)
                new_rect = py.Rect(x, y, 32, 32)

                if all(not new_rect.colliderect(py.Rect(px, py_, 32, 32).inflate(100, 100)) for px, py_ in placed_positions) and \
                   all(not new_rect.colliderect(p.rect.inflate(100, 100)) for p in self.players):

                    placed_positions.append((x, y))
                    weapon_type = random.choice([w for w in CONSTANTS["weapons"]["types"] if w != "fist"])
                    weapon = Weapon(x, y, weapon_type=weapon_type)
                    self.weapons.append(weapon)

                    for _ in range(random.randint(1, 3)):
                        offset_x = random.randint(-80, 80)
                        offset_y = random.randint(-80, 80)
                        enemy_x = max(0, min(world_w - 40, x + offset_x))
                        enemy_y = max(0, min(world_h - 40, y + offset_y))
                        enemy = Enemy(self.weapons, self.players, pos=(enemy_x, enemy_y))
                        self.enemies.append(enemy)
                    break

    def handle_event(self, event):
        if self.winner_scene:
            self.winner_scene.handle_event(event)
            return

        if event.type == py.KEYDOWN:
            if event.key == py.K_SPACE:
                self.players[0].attack(self.enemies + self.players[1:], self.bullets, self.effects)
            elif event.key == py.K_RETURN:
                self.players[1].attack(self.enemies + self.players[:1], self.bullets, self.effects)
            elif event.key == py.K_q:
                self.players[0].switch_weapon(-1)
            elif event.key == py.K_e:
                self.players[0].switch_weapon(1)
            elif event.key == py.K_KP7:
                self.players[1].switch_weapon(-1)
            elif event.key == py.K_KP8:
                self.players[1].switch_weapon(1)

            elif event.key == py.K_r:
                self.players[0].drop_weapon(self.weapons)
            elif event.key == py.K_RCTRL:
                self.players[1].drop_weapon(self.weapons)

    def update(self):
        if self.winner_scene:
            return

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
            eff.update(self.enemies + self.players)
            if getattr(eff, "state", None) == "finished":
                self.effects.remove(eff)

        self.enemies = [e for e in self.enemies if e.health > 0]
        alive_players = [p for p in self.players if p.health > 0]
        if len(alive_players) == 1 and not self.finished:
            self.finished = True
            winner_index = self.players.index(alive_players[0]) + 1  # 1 или 2
            for i, player in enumerate(self.players):
                if player.health <= 0:
                    from scene_manager import SceneManager
                    from src.scenes.final_screen import WinScene
                    winner_index = 1 - i
                    SceneManager.get_instance().add("win", WinScene(winner_index, level_scene_name=self.level_id))
                    SceneManager.get_instance().set_scene("win")
                    return


    def render(self, screen):
        if self.winner_scene:
            self.winner_scene.render(screen)
            return

        bg_color = tuple(self.level_data.get("background_color", (40, 40, 40)))
        screen.fill(bg_color)

        for enemy in self.enemies:
            enemy.draw_scaled(screen, self.scale_pos)

        for weapon in self.weapons:
            pos = self.scale_pos(weapon.rect.topleft)
            rect = weapon.image.get_rect(topleft=pos)
            screen.blit(weapon.image, rect)

        for player in self.players:
            player.draw_scaled(screen, self.scale_pos)

        for bullet in self.bullets:
            pos = self.scale_pos(bullet.rect.topleft)
            rect = bullet.image.get_rect(topleft=pos)
            screen.blit(bullet.image, rect)

        for eff in self.effects[:]:
            if hasattr(eff, 'draw'):
                if isinstance(eff, MolotovEffect):
                    eff.draw(screen, self.scale_pos)
                else:
                    eff.draw(screen)

    def restart_level(self):
        self.set_player_choices(self.players[0].gender, self.players[1].gender)
        self.finished = False
        self.winner_scene = None

    def go_to_main_menu(self):
        from scene_manager import SceneManager
        manager = SceneManager.get_instance()
        manager.set_scene("main_menu")


