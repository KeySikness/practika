import pygame as py
import math
from config import CONSTANTS


class Bullet(py.sprite.Sprite):
    def __init__(self, start_pos, angle, damage, owner, params={}):
        super().__init__()
        size = params.get("size", [5, 5])
        color = params.get("color", [255, 255, 0])

        self.image = py.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=start_pos)

        self.angle = angle
        self.speed = params.get("speed", 10)
        self.damage = damage
        self.owner = owner

        rad = math.radians(self.angle)
        self.dx = self.speed * math.cos(rad)
        self.dy = self.speed * math.sin(rad)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def check_collision(self, targets):
        for target in targets:
            if target != self.owner and self.rect.colliderect(target.rect):
                target.health -= self.damage
                self.kill()
                break


class MolotovEffect:
    def __init__(self, position, params={}, explosion_image=None):
        self.position = position
        self.explosion_delay = params.get("explosion_delay", 800)
        self.fire_duration = params.get("fire_duration", 3000)
        self.radius = params.get("radius", 100)
        self.burn_interval = params.get("burn_interval", 300)
        self.explosion_damage = params.get("explosion_damage", 5)
        self.burn_damage = params.get("burn_damage", 1)

        self.explosion_time = py.time.get_ticks() + self.explosion_delay
        self.end_time = self.explosion_time + self.fire_duration
        self.state = 'waiting'
        self.last_burn_time = 0
        self.exploded = False

        # Загрузка изображения взрыва
        if explosion_image:
            self.explosion_image = py.image.load(explosion_image).convert_alpha()
            self.explosion_image = py.transform.scale(
                self.explosion_image,
                (self.radius * 2, self.radius * 2)
            )
        else:
            self.explosion_image = None

    def update(self, targets):
        now = py.time.get_ticks()

        if self.state == 'waiting' and now >= self.explosion_time:
            self.state = 'active'
            self.last_burn_time = now

            for target in targets:
                dx = target.rect.centerx - self.position[0]
                dy = target.rect.centery - self.position[1]
                if dx * dx + dy * dy <= self.radius * self.radius:
                    target.health -= self.explosion_damage
            self.exploded = True

        if self.state == 'active':
            if now >= self.end_time:
                self.state = 'finished'
                return

            if now - self.last_burn_time >= self.burn_interval:
                for target in targets:
                    dx = target.rect.centerx - self.position[0]
                    dy = target.rect.centery - self.position[1]
                    if dx * dx + dy * dy <= self.radius * self.radius:
                        target.health -= self.burn_damage
                self.last_burn_time = now

    def draw(self, surface, scale_func=None):
        pos = self.position
        if scale_func:
            pos = scale_func(self.position)

        if self.state == 'waiting':
            if not hasattr(self, 'molotov_image'):
                # Загрузка изображения молотова из конфига
                weapon_data = CONSTANTS["weapons"]["stats"].get("molotov", {})
                image_path = weapon_data.get("image", "assets/images/weapon/molotov.png")

                original_image = py.image.load(image_path).convert_alpha()
                self.molotov_image = py.transform.smoothscale(original_image, (30, 30))

            rect = self.molotov_image.get_rect(center=pos)
            surface.blit(self.molotov_image, rect)

        elif self.state == 'active':
            if self.explosion_image:
                rect = self.explosion_image.get_rect(center=pos)
                surface.blit(self.explosion_image, rect)
            else:
                radius_scaled = self.radius
                if scale_func:
                    sx = scale_func((self.position[0] + self.radius, self.position[1]))[0] - pos[0]
                    sy = scale_func((self.position[0], self.position[1] + self.radius))[1] - pos[1]
                    radius_scaled = int((sx + sy) / 2)

                s = py.Surface((radius_scaled * 2, radius_scaled * 2), py.SRCALPHA)
                py.draw.circle(s, (255, 0, 0, 100), (radius_scaled, radius_scaled), radius_scaled)
                surface.blit(s, (pos[0] - radius_scaled, pos[1] - radius_scaled))


class Boomerang(py.sprite.Sprite):
    def __init__(self, start_pos, owner, damage, params={}):
        super().__init__()
        weapon_data = CONSTANTS["weapons"]["stats"].get("boomerang", {})
        image_path = weapon_data.get("image", "assets/images/weapon/boomerang.png")

        size = params.get("size", [35, 35])
        image = py.image.load(image_path).convert_alpha()
        self.image = py.transform.scale(image, size)
        self.rect = self.image.get_rect(center=start_pos)

        self.owner = owner
        self.damage = damage
        self.spawn_time = py.time.get_ticks()
        self.max_time = params.get("max_time", 1500)
        self.angle = owner.facing_angle
        self.center_x, self.center_y = start_pos
        self.speed = params.get("speed", 5)
        self.radius = 0
        self.angular_speed = params.get("angular_speed", 0.2)
        self.current_angle = 0
        self.returning = False

        self.last_hit_times = {}
        self.hit_interval = params.get("hit_interval", 100)

    def update(self):
        now = py.time.get_ticks()
        elapsed = now - self.spawn_time

        if not self.returning:
            # по спирали
            self.radius += 1
            self.current_angle += self.angular_speed

            rad_facing = math.radians(self.angle)
            forward_dx = math.cos(rad_facing) * self.speed * (elapsed / 60)
            forward_dy = math.sin(rad_facing) * self.speed * (elapsed / 60)

            spiral_dx = self.radius * math.cos(self.current_angle)
            spiral_dy = self.radius * math.sin(self.current_angle)

            self.rect.centerx = self.center_x + forward_dx + spiral_dx
            self.rect.centery = self.center_y + forward_dy + spiral_dy

            if elapsed >= self.max_time:
                self.returning = True
        else:
            # к игроку
            target_x, target_y = self.owner.rect.center
            dir_x = target_x - self.rect.centerx
            dir_y = target_y - self.rect.centery
            distance = math.hypot(dir_x, dir_y)

            if distance < 15:
                if hasattr(self.owner, 'active_boomerang'):
                    self.owner.active_boomerang = None
                self.kill()
                return

            move_x = dir_x / distance * self.speed
            move_y = dir_y / distance * self.speed

            self.rect.centerx += move_x
            self.rect.centery += move_y

    def check_collision(self, targets):
        now = py.time.get_ticks()
        for target in targets:
            if target != self.owner and self.rect.colliderect(target.rect):
                last_hit = self.last_hit_times.get(target, 0)
                if now - last_hit >= self.hit_interval:
                    target.health -= self.damage
                    self.last_hit_times[target] = now


class Yoyo(py.sprite.Sprite):
    def __init__(self, owner, damage, targets, params={}):
        super().__init__()
        # Загрузка изображения из конфига
        weapon_data = CONSTANTS["weapons"]["stats"].get("yoyo", {})
        image_path = weapon_data.get("image", "assets/images/weapon/yoyo.png")

        size = params.get("size", [30, 30])
        image = py.image.load(image_path).convert_alpha()
        self.image = py.transform.scale(image, size)
        self.rect = self.image.get_rect(center=owner.rect.center)

        self.owner = owner
        self.damage = damage
        self.targets = targets

        self.speed = params.get("speed", 10)
        self.max_distance = params.get("max_distance", 200)
        self.origin = py.Vector2(owner.rect.center)
        self.position = py.Vector2(owner.rect.center)
        self.direction = py.Vector2(
            math.cos(math.radians(owner.facing_angle)),
            math.sin(math.radians(owner.facing_angle))
        )

        self.state = "outgoing"
        self.stuck_target = None
        self.stuck_start_time = None
        self.stun_duration = params.get("stun_duration", 1200)
        self.stun_end_time = 0
        self.pull_speed = params.get("pull_speed", 30)

    def update(self):
        now = py.time.get_ticks()

        if self.state == "outgoing":
            self.position += self.direction * self.speed
            self.rect.center = self.position

            if self.position.distance_to(self.origin) >= self.max_distance:
                self.state = "returning"

            for target in self.targets:
                if target == self.owner or getattr(target, "health", None) is None or target.health <= 0:
                    continue
                if self.rect.colliderect(target.rect):
                    target.health -= self.damage
                    target.stunned = True
                    if hasattr(target, 'stun_timer'):
                        target.stun_timer = now + self.stun_duration
                    else:
                        target.stun_end_time = now + self.stun_duration

                    target_pos = py.Vector2(target.rect.center)
                    owner_pos = py.Vector2(self.owner.rect.center)
                    pull_vector = owner_pos - target_pos
                    if pull_vector.length() > 0:
                        pull_vector = pull_vector.normalize() * self.pull_speed
                        target.rect.center += pull_vector

                    self.stuck_target = target
                    self.stun_end_time = now + self.stun_duration
                    self.state = "stuck"
                    break

        elif self.state == "stuck":
            self.state = "returning"

        elif self.state == "returning":
            direction_to_owner = (py.Vector2(self.owner.rect.center) - self.position)
            distance = direction_to_owner.length()

            if distance < self.speed:
                self.kill()
                self.owner.active_yoyo = None
            else:
                direction_to_owner.normalize_ip()
                self.position += direction_to_owner * self.speed
                self.rect.center = self.position