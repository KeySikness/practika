import pygame as py
import random
import json
import os

from sprites.player import Player
from sprites.enemies import Enemy
from sprites.weapons import Weapon
from sprites.map import Map
from sprites.projectiles import MolotovEffect
from config import CONSTANTS, LEVELS_DIR
from audio_manager import AudioManager
ENEMY_CONFIG = CONSTANTS["enemy"]


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

        self.window_size = (1600, 900)
        self.scale_x = 1
        self.scale_y = 1

        self.playing_track = AudioManager.get_instance().play_random_level_music()

        self.load_map()

    def load_level_data(self):
        level_file = os.path.join(LEVELS_DIR, f"{self.level_id}.json")
        with open(level_file, "r", encoding="utf-8") as f:
            self.level_data = json.load(f)

    def load_map(self):
        self.map = Map(self.level_data["map"])

    def is_point_inside_map(self, x, y):
        return self.map.is_walkable(x, y)

    def on_enter(self):
        self.finished = False
        self.playing_track = AudioManager.get_instance().play_random_level_music()

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

        num_weapons = random.randint(3, 20)
        placed_positions = []

        world_w, world_h = self.level_data["world_size"]

        for _ in range(num_weapons):
            import pygame as py
            for _ in range(100):
                x = random.randint(32, world_w - 32)
                y = random.randint(32, world_h - 32)
                new_rect = py.Rect(x, y, 32, 32)

                if all(not new_rect.colliderect(py.Rect(px, py_, 32, 32).inflate(100, 100)) for px, py_ in
                       placed_positions) and \
                        all(not new_rect.colliderect(p.rect.inflate(100, 100)) for p in self.players):

                    points_to_check = [
                        (x + 16, y + 16), # центр
                        (x, y), # верх лев
                        (x + 31, y), # верх прав
                        (x, y + 31), # ниж лев
                        (x + 31, y + 31) # ниж прав
                    ]

                    if all(self.map.is_walkable(px, py) for px, py in points_to_check):
                        placed_positions.append((x, y))
                        weapon_type = random.choice([w for w in CONSTANTS["weapons"]["types"] if w != "fist"])
                        weapon = Weapon(x, y, weapon_type=weapon_type)
                        self.weapons.append(weapon)

                        for _ in range(random.randint(1, 3)):
                            max_enemy_attempts = 30
                            for attempt in range(max_enemy_attempts):
                                offset_x = random.randint(-80, 80)
                                offset_y = random.randint(-80, 80)
                                enemy_x = max(0, min(world_w - 40, x + offset_x))
                                enemy_y = max(0, min(world_h - 40, y + offset_y))

                                enemy_points = [
                                    (enemy_x + 20, enemy_y + 20),
                                    (enemy_x, enemy_y),
                                    (enemy_x + 39, enemy_y),
                                    (enemy_x, enemy_y + 39),
                                    (enemy_x + 39, enemy_y + 39)
                                ]
                                if not all(self.map.is_walkable(px, py) for px, py in enemy_points):
                                    continue

                                temp_enemy = Enemy(self.weapons, self.players, pos=(enemy_x, enemy_y))
                                overlaps = any(
                                    temp_enemy.rect.colliderect(e.rect.inflate(-10, -10)) for e in self.enemies)
                                too_close_to_players = any(
                                    (temp_enemy.rect.centerx - p.rect.centerx) ** 2 + (
                                                temp_enemy.rect.centery - p.rect.centery) ** 2 < ENEMY_CONFIG[
                                        "min_spawn_distance"] ** 2
                                    for p in self.players
                                )
                                if not overlaps and not too_close_to_players:
                                    self.enemies.append(temp_enemy)
                                    break
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
            original_rect = player.rect.copy()
            player.rect.x += player.dx
            player.rect.y += player.dy

            corners = [
                player.rect.topleft,
                player.rect.topright,
                player.rect.bottomleft,
                player.rect.bottomright
            ]

            if not all(self.is_point_inside_map(x, y) for (x, y) in corners):
                player.rect = original_rect
            player.update()

        for enemy in self.enemies:
            enemy.update(self.players, self.level_data["world_size"], self.map)

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

        screen.fill((0, 0, 0))

        screen_w, screen_h = self.window_size
        half_width = screen_w // 2
        world_w, world_h = self.level_data["world_size"]

        views = [(0, self.players[0]), (half_width, self.players[1])]

        for x_offset, player in views:
            camera_offset = self.get_camera_offset(player.rect, (half_width, screen_h), (world_w, world_h))

            view_surface = py.Surface((half_width, screen_h))
            view_surface.fill(self.level_data.get("background_color", (40, 40, 40)))

            self.map.draw(view_surface, -camera_offset)

            for weapon in self.weapons:
                pos = py.Vector2(weapon.rect.topleft) - camera_offset
                weapon.draw_on_map(view_surface, pos=pos)

            for bullet in self.bullets:
                pos = py.Vector2(bullet.rect.topleft) - camera_offset
                view_surface.blit(bullet.image, pos)

            for enemy in self.enemies:
                enemy.draw(view_surface, camera_offset)

            for eff in self.effects:
                if hasattr(eff, "draw"):
                    if isinstance(eff, MolotovEffect):
                        eff.draw(view_surface, lambda p: (p[0] - camera_offset.x, p[1] - camera_offset.y))
                    else:
                        eff.draw(view_surface)

            for p in self.players:
                if p.health > 0:
                    original_rect = p.rect.copy()
                    p.rect = p.rect.move(-camera_offset.x, -camera_offset.y)
                    p.draw(view_surface)
                    p.rect = original_rect

            screen.blit(view_surface, (x_offset, 0))
        py.draw.line(screen, (255, 255, 255), (half_width, 0), (half_width, screen_h), 2)

    def restart_level(self):
        self.set_player_choices(self.players[0].gender, self.players[1].gender)
        self.finished = False
        self.winner_scene = None

    def go_to_main_menu(self):
        from scene_manager import SceneManager
        manager = SceneManager.get_instance()
        manager.set_scene("main_menu")

    def get_camera_offset(self, target_rect, screen_size, world_size):
        cam_x = target_rect.centerx - screen_size[0] // 2
        cam_y = target_rect.centery - screen_size[1] // 2
        cam_x = max(0, min(cam_x, world_size[0] - screen_size[0]))
        cam_y = max(0, min(cam_y, world_size[1] - screen_size[1]))

        return py.Vector2(cam_x, cam_y)



