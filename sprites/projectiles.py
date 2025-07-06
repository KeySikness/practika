import pygame as py
import math
import time
from config import CONSTANTS

class Bullet(py.sprite.Sprite):
    def __init__(self, start_pos, angle, damage, owner):
        super().__init__()
        self.image = py.Surface((5, 5))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=start_pos)
        self.angle = angle
        self.speed = 10
        self.damage = damage
        self.owner = owner

        rad = math.radians(self.angle)
        self.dx = self.speed * math.cos(rad)
        self.dy = -self.speed * math.sin(rad)

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
    def __init__(self, position,
                 explosion_damage,
                 burn_damage,
                 explosion_delay=800,
                 fire_duration=3000,
                 radius=100,
                 burn_interval=300):
        self.position = position
        self.explosion_time = py.time.get_ticks() + explosion_delay
        self.end_time = self.explosion_time + fire_duration
        self.radius = radius
        self.state = 'waiting'
        self.explosion_damage = explosion_damage
        self.burn_damage = burn_damage
        self.burn_interval = burn_interval
        self.last_burn_time = 0
        self.exploded = False

    def update(self, targets):
        now = py.time.get_ticks()

        if self.state == 'waiting' and now >= self.explosion_time:
            self.state = 'active'
            self.last_burn_time = now

            for target in targets:
                dx = target.rect.centerx - self.position[0]
                dy = target.rect.centery - self.position[1]
                if dx*dx + dy*dy <= self.radius*self.radius:
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
                    if dx*dx + dy*dy <= self.radius*self.radius:
                        target.health -= self.burn_damage
                self.last_burn_time = now

    def draw(self, surface):
        if self.state == 'waiting':
            py.draw.circle(surface, (255, 100, 0), self.position, 10)
        elif self.state == 'active':
            s = py.Surface((self.radius * 2, self.radius * 2), py.SRCALPHA)
            py.draw.circle(s, (255, 0, 0, 100), (self.radius, self.radius), self.radius)
            surface.blit(s, (self.position[0] - self.radius, self.position[1] - self.radius))

class Boomerang(py.sprite.Sprite):
    def __init__(self, start_pos, owner, damage=8, max_time=1500):
        super().__init__()
        self.image = py.Surface((20, 20), py.SRCALPHA)
        py.draw.polygon(self.image, (0, 200, 255), [(10, 0), (20, 10), (10, 20), (0, 10)])
        self.rect = self.image.get_rect(center=start_pos)

        self.owner = owner
        self.damage = damage
        self.spawn_time = py.time.get_ticks()
        self.max_time = max_time
        self.angle = owner.facing_angle
        self.center_x, self.center_y = start_pos
        self.speed = 5
        self.radius = 0
        self.angular_speed = 0.2
        self.current_angle = 0
        self.returning = False

        self.last_hit_times = {}
        self.hit_interval = 80  # мс между ударами

    def update(self):
        now = py.time.get_ticks()
        elapsed = now - self.spawn_time

        if not self.returning:
            # движение по спирали
            self.radius += 1
            self.current_angle += self.angular_speed

            rad_facing = math.radians(self.angle)
            forward_dx = math.cos(rad_facing) * self.speed * (elapsed / 60)
            forward_dy = -math.sin(rad_facing) * self.speed * (elapsed / 60)

            spiral_dx = self.radius * math.cos(self.current_angle)
            spiral_dy = self.radius * math.sin(self.current_angle)

            self.rect.centerx = self.center_x + forward_dx + spiral_dx
            self.rect.centery = self.center_y + forward_dy + spiral_dy

            if elapsed >= self.max_time:
                self.returning = True
        else:
            # возврат к игроку
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
    def __init__(self, owner, damage, targets, max_distance=200, speed=10):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.targets = targets

        self.image = py.Surface((20, 20), py.SRCALPHA)
        py.draw.circle(self.image, (255, 255, 255), (10, 10), 10)
        self.rect = self.image.get_rect(center=owner.rect.center)

        self.speed = speed
        self.max_distance = max_distance
        self.origin = py.Vector2(owner.rect.center)
        self.position = py.Vector2(owner.rect.center)
        self.direction = py.Vector2(math.cos(math.radians(owner.facing_angle)),
                                    -math.sin(math.radians(owner.facing_angle)))

        self.state = "outgoing"  # outgoing, stuck, returning
        self.stuck_target = None
        self.stuck_start_time = None
        self.stun_duration = 1200
        self.stun_end_time = 0
        self.pull_speed = 30

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