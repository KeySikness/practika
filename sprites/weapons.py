import pygame as py
import random
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
        self.image = self.create_image(weapon_type)
        self.rect = self.image.get_rect(center=(x, y))
        self.cooldown = CONSTANTS["weapons"]["stats"][weapon_type]["cooldown"]
        self.last_attack_time = py.time.get_ticks()
        self.damage = CONSTANTS["weapons"]["stats"][weapon_type]["damage"]

    def create_image(self, weapon_type):
        color_map = {
            "fist": (255, 0, 0),  # красный
            "shotgun": (0, 255, 0),  # зеленый
            "melee_bat": (0, 0, 255),  # синий
            "melee_axe": (255, 255, 0),  # желтый
            "melee_knife": (255, 165, 0),  # оранжевый
            "melee_club": (128, 0, 128), # фиолетовый
            "molotov": (5, 247, 138), # бирюзовый
            "boomerang": (0, 0, 0),
            "yoyo": (255,255,255)
        }
        color = color_map.get(weapon_type, (255, 255, 255))  # Белый цвет
        image = py.Surface((32, 32))
        image.fill(color)
        return image

    def attack(self, player, targets, bullets_group, effects_list=None):
        now = py.time.get_ticks()
        if now - self.last_attack_time < self.cooldown:
            return

        if self.weapon_type == "yoyo" and getattr(player, "weapon_in_use", False):
            return

        self.last_attack_time = now

        if self.weapon_type == "shotgun":
            spread_angles = [-20, -7, 7, 20]  # углы разброса
            for angle_offset in spread_angles:
                bullet_angle = player.facing_angle + angle_offset
                bullet = Bullet(player.rect.center, bullet_angle, self.damage, owner=player)
                bullets_group.add(bullet)

        elif self.weapon_type == "boomerang":
            if player.active_boomerang is None:
                boomerang = Boomerang(player.rect.center, owner=player, damage=self.damage)
                bullets_group.add(boomerang)
                player.active_boomerang = boomerang

        elif self.weapon_type == "molotov":
            effect = MolotovEffect(
            player.rect.center,
            explosion_damage=5,
            burn_damage=1
            )
            effects_list.append(effect)


        elif self.weapon_type == "yoyo":
            if getattr(player, "active_yoyo", None) is None:
                yoyo = Yoyo(owner=player, damage=5, targets=targets)
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
