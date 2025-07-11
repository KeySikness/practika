import pygame as py
import math
from config import CONSTANTS
from sprites.projectiles import Bullet, MolotovEffect, Boomerang, Yoyo


class Weapon(py.sprite.Sprite):
    def __init__(self, x, y, weapon_type="fist"):
        super().__init__()
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
        self.yoyo_instance = None
        self.owner = None

        weapon_data = CONSTANTS["weapons"]["stats"].get(weapon_type, {})

        self.image = self.create_image(weapon_type, weapon_data)
        self.rect = self.image.get_rect(center=(x, y))
        self.cooldown = weapon_data.get("cooldown", 500)
        self.last_attack_time = py.time.get_ticks()
        self.damage = weapon_data.get("damage", 1)

    def create_image(self, weapon_type, weapon_data):
        image_path = weapon_data.get("image")
        size = weapon_data.get("size", (42, 42))

        if image_path:
            image = py.image.load(image_path).convert_alpha()
            return py.transform.scale(image, size)
        if weapon_type == "fist":
            image = py.Surface(size, py.SRCALPHA)
            image.fill((0, 0, 0, 0))
            return image

        image = py.Surface(size, py.SRCALPHA)
        return image

    def draw_on_map(self, surface, pos=None):
        if pos is None:
            pos = self.rect.topleft
        surface.blit(self.image, pos)

    def attack(self, player, targets, bullets_group, effects_list=None):
        now = py.time.get_ticks()
        if now - self.last_attack_time < self.cooldown:
            return

        if self.weapon_type == "yoyo" and getattr(player, "weapon_in_use", False):
            return

        self.last_attack_time = now
        weapon_data = CONSTANTS["weapons"]["stats"].get(self.weapon_type, {})
        projectile_params = weapon_data.get("projectile", {})

        if self.weapon_type == "shotgun":
            spread_angles = projectile_params.get("spread_angles", [-20, -7, 7, 20])
            for angle_offset in spread_angles:
                bullet_angle = player.facing_angle + angle_offset
                bullet = Bullet(
                    player.rect.center,
                    bullet_angle,
                    self.damage,
                    owner=player,
                    params=projectile_params
                )
                bullets_group.add(bullet)

        elif self.weapon_type == "boomerang":
            if player.active_boomerang is None:
                boomerang = Boomerang(
                    player.rect.center,
                    owner=player,
                    damage=self.damage,
                    params=projectile_params
                )
                bullets_group.add(boomerang)
                player.active_boomerang = boomerang

        elif self.weapon_type == "molotov":
            effect = MolotovEffect(
                player.rect.center,
                params=projectile_params,
                explosion_image=weapon_data.get("explosion")
            )
            effects_list.append(effect)

        elif self.weapon_type == "yoyo":
            if getattr(player, "active_yoyo", None) is None:
                yoyo = Yoyo(
                    owner=player,
                    damage=self.damage,
                    targets=targets,
                    params=projectile_params
                )
                bullets_group.add(yoyo)
                player.active_yoyo = yoyo

        else:
            attack_rect = player.rect.copy()
            offset = 40
            angle_rad = math.radians(player.facing_angle)
            attack_rect.x += int(math.cos(angle_rad) * offset)
            attack_rect.y -= int(math.sin(angle_rad) * offset)

            for target in targets:
                if attack_rect.colliderect(target.rect):
                    target.health -= self.damage