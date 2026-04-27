"""
BGMI-Inspired Battle Royale Game using Pygame
=============================================
A top-down battle royale shooter game inspired by BGMI (Battlegrounds Mobile India)
Features: Player movement, shooting, enemies, safe zone, loot, health system, minimap, UI
Author: Claude AI
Lines: 1000+
"""

import pygame
import random
import math
import sys
import time
from pygame import mixer

# ─────────────────────────────────────────────
#  INITIALIZATION
# ─────────────────────────────────────────────
pygame.init()
mixer.init()

# ─────────────────────────────────────────────
#  CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60
TITLE = "BGMI - Battle Royale (Pygame)"

# Map size (larger than screen for scrolling)
MAP_WIDTH = 3000
MAP_HEIGHT = 3000

# Colors
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
RED         = (220, 50, 50)
GREEN       = (50, 200, 80)
DARK_GREEN  = (30, 120, 50)
BLUE        = (50, 100, 220)
YELLOW      = (255, 215, 0)
ORANGE      = (255, 140, 0)
CYAN        = (0, 220, 220)
PURPLE      = (150, 50, 220)
BROWN       = (139, 90, 43)
GRAY        = (120, 120, 120)
DARK_GRAY   = (60, 60, 60)
LIGHT_GRAY  = (180, 180, 180)
SAND        = (210, 180, 140)
DARK_BLUE   = (10, 20, 60)
PINK        = (255, 105, 180)
LIME        = (150, 255, 50)
TEAL        = (0, 180, 150)

# Player settings
PLAYER_SPEED       = 4
PLAYER_HEALTH      = 100
PLAYER_SIZE        = 18
PLAYER_COLOR       = (50, 180, 255)
BULLET_SPEED       = 14
BULLET_DAMAGE      = 20
BULLET_SIZE        = 5
SHOOT_COOLDOWN     = 15   # frames
RELOAD_TIME        = 90   # frames
MAG_SIZE           = 30

# Enemy settings
ENEMY_SPEED        = 2
ENEMY_HEALTH       = 80
ENEMY_SIZE         = 16
ENEMY_COLOR        = (220, 60, 60)
ENEMY_SHOOT_RANGE  = 300
ENEMY_SIGHT_RANGE  = 400
ENEMY_SHOOT_DELAY  = 60
NUM_ENEMIES        = 25

# Safe zone settings
ZONE_SHRINK_INTERVAL = 600   # frames between shrinks
ZONE_DAMAGE          = 0.5   # damage per frame outside zone
ZONE_MIN_RADIUS      = 80

# Loot settings
NUM_LOOT_CRATES  = 30
NUM_MEDKITS      = 20
NUM_AMMO_BOXES   = 25
NUM_ARMOR_BOXES  = 10

# ─────────────────────────────────────────────
#  SCREEN SETUP
# ─────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# ─────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────
font_large  = pygame.font.SysFont("consolas", 36, bold=True)
font_medium = pygame.font.SysFont("consolas", 22, bold=True)
font_small  = pygame.font.SysFont("consolas", 16)
font_tiny   = pygame.font.SysFont("consolas", 13)

# ─────────────────────────────────────────────
#  CAMERA
# ─────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_x, target_y):
        self.offset_x = target_x - SCREEN_WIDTH // 2
        self.offset_y = target_y - SCREEN_HEIGHT // 2
        self.offset_x = max(0, min(self.offset_x, MAP_WIDTH - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, MAP_HEIGHT - SCREEN_HEIGHT))

    def apply(self, x, y):
        return x - self.offset_x, y - self.offset_y

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y, rect.w, rect.h)

# ─────────────────────────────────────────────
#  BULLET CLASS
# ─────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, angle, owner="player", damage=BULLET_DAMAGE):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = BULLET_SPEED
        self.damage = damage
        self.owner = owner
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.alive = True
        self.trail = []
        self.color = YELLOW if owner == "player" else RED
        self.size = BULLET_SIZE

    def update(self):
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        if not (0 <= self.x <= MAP_WIDTH and 0 <= self.y <= MAP_HEIGHT):
            self.alive = False

    def draw(self, surface, camera):
        for i, pos in enumerate(self.trail):
            sx, sy = camera.apply(*pos)
            alpha = int(255 * (i + 1) / len(self.trail))
            trail_color = (*self.color[:3], alpha)
            pygame.draw.circle(surface, self.color, (sx, sy), max(1, self.size - (len(self.trail) - i)))
        sx, sy = camera.apply(int(self.x), int(self.y))
        pygame.draw.circle(surface, WHITE, (sx, sy), self.size)
        pygame.draw.circle(surface, self.color, (sx, sy), self.size - 1)

# ─────────────────────────────────────────────
#  PARTICLE CLASS (Visual effects)
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, speed=3, lifetime=30, size=4):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply(int(self.x), int(self.y))
        alpha_ratio = self.lifetime / self.max_lifetime
        size = max(1, int(self.size * alpha_ratio))
        r = min(255, int(self.color[0]))
        g = min(255, int(self.color[1]))
        b = min(255, int(self.color[2]))
        pygame.draw.circle(surface, (r, g, b), (sx, sy), size)

# ─────────────────────────────────────────────
#  LOOT ITEM CLASS
# ─────────────────────────────────────────────
class LootItem:
    TYPES = {
        "medkit":   {"color": PINK,   "size": 12, "symbol": "+"},
        "ammo":     {"color": YELLOW, "size": 10, "symbol": "A"},
        "armor":    {"color": CYAN,   "size": 11, "symbol": "V"},
        "weapon":   {"color": ORANGE, "size": 13, "symbol": "W"},
    }

    def __init__(self, x, y, loot_type="medkit"):
        self.x = x
        self.y = y
        self.type = loot_type
        self.info = self.TYPES.get(loot_type, self.TYPES["medkit"])
        self.rect = pygame.Rect(x - self.info["size"], y - self.info["size"],
                                self.info["size"] * 2, self.info["size"] * 2)
        self.alive = True
        self.bob_timer = random.uniform(0, math.pi * 2)
        self.pulse = 0

    def update(self):
        self.bob_timer += 0.05
        self.pulse = (math.sin(self.bob_timer) + 1) / 2

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.x, self.y)
        sy_bob = sy + int(math.sin(self.bob_timer) * 3)
        size = self.info["size"]
        glow_size = size + int(self.pulse * 5)
        glow_color = tuple(min(255, c + 80) for c in self.info["color"])
        pygame.draw.circle(surface, glow_color, (sx, sy_bob), glow_size, 2)
        pygame.draw.rect(surface, DARK_GRAY, (sx - size, sy_bob - size, size * 2, size * 2), border_radius=4)
        pygame.draw.rect(surface, self.info["color"], (sx - size + 2, sy_bob - size + 2,
                          size * 2 - 4, size * 2 - 4), border_radius=3)
        label = font_tiny.render(self.info["symbol"], True, WHITE)
        surface.blit(label, (sx - label.get_width() // 2, sy_bob - label.get_height() // 2))

# ─────────────────────────────────────────────
#  TREE / OBSTACLE CLASS
# ─────────────────────────────────────────────
class Tree:
    def __init__(self, x, y, size=None):
        self.x = x
        self.y = y
        self.size = size or random.randint(18, 35)
        self.color = random.choice([DARK_GREEN, (20, 100, 40), (40, 130, 60)])
        self.trunk_color = BROWN
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.x, self.y)
        # Trunk
        pygame.draw.rect(surface, self.trunk_color,
                          (sx - 4, sy, 8, 14), border_radius=2)
        # Canopy
        pygame.draw.circle(surface, self.trunk_color, (sx, sy), self.size + 2)
        pygame.draw.circle(surface, self.color, (sx, sy), self.size)
        pygame.draw.circle(surface, tuple(min(255, c + 40) for c in self.color),
                           (sx - self.size // 4, sy - self.size // 4),
                           self.size // 3)

# ─────────────────────────────────────────────
#  BUILDING / COVER CLASS
# ─────────────────────────────────────────────
class Building:
    def __init__(self, x, y, w=None, h=None):
        self.x = x
        self.y = y
        self.w = w or random.randint(60, 120)
        self.h = h or random.randint(60, 120)
        self.color = random.choice([GRAY, DARK_GRAY, (100, 90, 80), (110, 100, 90)])
        self.roof_color = tuple(max(0, c - 30) for c in self.color)
        self.rect = pygame.Rect(x - self.w // 2, y - self.h // 2, self.w, self.h)

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.x - self.w // 2, self.y - self.h // 2)
        # Shadow
        pygame.draw.rect(surface, (30, 30, 30), (sx + 4, sy + 4, self.w, self.h), border_radius=3)
        # Body
        pygame.draw.rect(surface, self.color, (sx, sy, self.w, self.h), border_radius=3)
        # Roof accent
        pygame.draw.rect(surface, self.roof_color, (sx + 4, sy + 4, self.w - 8, self.h - 8),
                         border_radius=2)
        # Windows
        for wy in range(2):
            for wx in range(2):
                wx_pos = sx + 10 + wx * (self.w // 2 - 10)
                wy_pos = sy + 10 + wy * (self.h // 2 - 10)
                pygame.draw.rect(surface, DARK_BLUE, (wx_pos, wy_pos, 14, 10), border_radius=2)
                pygame.draw.rect(surface, CYAN, (wx_pos + 2, wy_pos + 2, 5, 3))

# ─────────────────────────────────────────────
#  ENEMY CLASS
# ─────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.health = ENEMY_HEALTH
        self.max_health = ENEMY_HEALTH
        self.size = ENEMY_SIZE
        self.color = ENEMY_COLOR
        self.speed = ENEMY_SPEED + random.uniform(-0.5, 0.5)
        self.alive = True
        self.shoot_cooldown = random.randint(0, ENEMY_SHOOT_DELAY)
        self.state = "patrol"   # patrol, chase, shoot
        self.patrol_target = (random.randint(100, MAP_WIDTH - 100),
                               random.randint(100, MAP_HEIGHT - 100))
        self.bullets = []
        self.angle = 0
        self.hit_flash = 0
        self.kill_count = 0

    def update(self, player, obstacles):
        if not self.alive:
            return

        if self.hit_flash > 0:
            self.hit_flash -= 1

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # State machine
        if dist < ENEMY_SIGHT_RANGE:
            if dist < ENEMY_SHOOT_RANGE:
                self.state = "shoot"
            else:
                self.state = "chase"
        else:
            self.state = "patrol"

        if self.state == "chase" or self.state == "shoot":
            self.angle = math.atan2(dy, dx)

        # Movement
        if self.state == "patrol":
            pdx = self.patrol_target[0] - self.x
            pdy = self.patrol_target[1] - self.y
            pdist = math.hypot(pdx, pdy)
            if pdist < 20:
                self.patrol_target = (random.randint(100, MAP_WIDTH - 100),
                                       random.randint(100, MAP_HEIGHT - 100))
            else:
                move_angle = math.atan2(pdy, pdx)
                self.x += math.cos(move_angle) * self.speed * 0.5
                self.y += math.sin(move_angle) * self.speed * 0.5

        elif self.state == "chase":
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

        # Clamp to map
        self.x = max(self.size, min(MAP_WIDTH - self.size, self.x))
        self.y = max(self.size, min(MAP_HEIGHT - self.size, self.y))

        # Shooting
        if self.state == "shoot":
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = ENEMY_SHOOT_DELAY + random.randint(-10, 20)
                scatter = random.uniform(-0.15, 0.15)
                b = Bullet(self.x, self.y, self.angle + scatter, owner="enemy", damage=15)
                self.bullets.append(b)

        # Update enemy bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 8
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.apply(int(self.x), int(self.y))
        # Draw direction indicator
        end_x = sx + int(math.cos(self.angle) * (self.size + 8))
        end_y = sy + int(math.sin(self.angle) * (self.size + 8))
        pygame.draw.line(surface, ORANGE, (sx, sy), (end_x, end_y), 2)

        # Body
        color = WHITE if self.hit_flash > 0 else self.color
        pygame.draw.circle(surface, DARK_GRAY, (sx + 2, sy + 2), self.size)
        pygame.draw.circle(surface, color, (sx, sy), self.size)
        # Head detail
        pygame.draw.circle(surface, tuple(max(0, c - 40) for c in color), (sx, sy - 4), 7)
        # Eyes
        eye_angle = self.angle
        ex = sx + int(math.cos(eye_angle - 0.4) * 6)
        ey = sy + int(math.sin(eye_angle - 0.4) * 6)
        pygame.draw.circle(surface, RED, (ex, ey), 2)

        # Health bar
        bar_w = 36
        bar_h = 5
        bx = sx - bar_w // 2
        by = sy - self.size - 10
        pygame.draw.rect(surface, DARK_GRAY, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(surface, RED, (bx, by, bar_w, bar_h))
        hp_ratio = self.health / self.max_health
        pygame.draw.rect(surface, GREEN, (bx, by, int(bar_w * hp_ratio), bar_h))

        # Bullets
        for b in self.bullets:
            b.draw(surface, camera)

# ─────────────────────────────────────────────
#  PLAYER CLASS
# ─────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.armor = 0
        self.max_armor = 100
        self.size = PLAYER_SIZE
        self.color = PLAYER_COLOR
        self.speed = PLAYER_SPEED
        self.alive = True
        self.angle = 0.0

        # Weapon stats
        self.ammo = MAG_SIZE
        self.max_ammo = MAG_SIZE
        self.reserve_ammo = 90
        self.shoot_cooldown = 0
        self.reload_timer = 0
        self.reloading = False
        self.kills = 0
        self.shots_fired = 0
        self.shots_hit = 0

        # Inventory
        self.medkits = 2
        self.weapon = "M416"

        self.bullets = []
        self.particles = []
        self.hit_flash = 0
        self.footstep_timer = 0
        self.moving = False
        self.last_pos = (x, y)

    def handle_input(self, keys):
        vx, vy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    vy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  vy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  vx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx += self.speed

        # Normalize diagonal movement
        if vx != 0 and vy != 0:
            factor = 1 / math.sqrt(2)
            vx *= factor
            vy *= factor

        self.x += vx
        self.y += vy
        self.x = max(self.size, min(MAP_WIDTH - self.size, self.x))
        self.y = max(self.size, min(MAP_HEIGHT - self.size, self.y))

        self.moving = (vx != 0 or vy != 0)

        # Reload
        if keys[pygame.K_r] and not self.reloading and self.ammo < self.max_ammo and self.reserve_ammo > 0:
            self.reloading = True
            self.reload_timer = RELOAD_TIME

        # Use medkit
        if keys[pygame.K_e] and self.medkits > 0 and self.health < self.max_health:
            self.health = min(self.max_health, self.health + 40)
            self.medkits -= 1
            for _ in range(12):
                self.particles.append(Particle(self.x, self.y, PINK, speed=2, lifetime=25))

    def shoot(self, target_x, target_y, camera):
        if self.reloading or self.shoot_cooldown > 0 or self.ammo <= 0:
            return
        # Convert screen coords to world coords
        wx = target_x + camera.offset_x
        wy = target_y + camera.offset_y
        self.angle = math.atan2(wy - self.y, wx - self.x)
        # Slight spread
        spread = random.uniform(-0.04, 0.04)
        b = Bullet(self.x, self.y, self.angle + spread, owner="player")
        self.bullets.append(b)
        self.ammo -= 1
        self.shots_fired += 1
        self.shoot_cooldown = SHOOT_COOLDOWN
        # Muzzle flash particles
        for _ in range(6):
            self.particles.append(Particle(self.x + math.cos(self.angle) * self.size,
                                           self.y + math.sin(self.angle) * self.size,
                                           YELLOW, speed=3, lifetime=10, size=3))

    def update(self, mouse_pos, camera):
        # Aim direction
        wx = mouse_pos[0] + camera.offset_x
        wy = mouse_pos[1] + camera.offset_y
        self.angle = math.atan2(wy - self.y, wx - self.x)

        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.reloading:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                needed = self.max_ammo - self.ammo
                reloaded = min(needed, self.reserve_ammo)
                self.ammo += reloaded
                self.reserve_ammo -= reloaded
                self.reloading = False

        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Footstep particles
        if self.moving:
            self.footstep_timer += 1
            if self.footstep_timer % 15 == 0:
                self.particles.append(Particle(self.x, self.y, SAND, speed=0.5, lifetime=20, size=3))

        # Update bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

# ─────────────────────────────────────────────
#  WORLD SETUP
# ─────────────────────────────────────────────
camera = Camera()

player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

enemies = [Enemy(random.randint(100, MAP_WIDTH-100),
                 random.randint(100, MAP_HEIGHT-100)) for _ in range(NUM_ENEMIES)]

trees = [Tree(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)) for _ in range(120)]
buildings = [Building(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)) for _ in range(25)]

loot_items = []
for _ in range(NUM_MEDKITS):
    loot_items.append(LootItem(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT), "medkit"))
for _ in range(NUM_AMMO_BOXES):
    loot_items.append(LootItem(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT), "ammo"))
for _ in range(NUM_ARMOR_BOXES):
    loot_items.append(LootItem(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT), "armor"))


zone_radius = 1200
zone_center = [MAP_WIDTH // 2, MAP_HEIGHT // 2]
zone_timer = 0

running = True
while running:
    clock.tick(FPS)
    screen.fill((34, 139, 34))  # grass

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot(*pygame.mouse.get_pos(), camera)

    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update(pygame.mouse.get_pos(), camera)

    camera.update(player.x, player.y)

    # Update enemies
    for enemy in enemies:
        enemy.update(player, [])

    # Bullet collision
    for bullet in player.bullets:
        for enemy in enemies:
            if enemy.alive:
                dist = math.hypot(enemy.x - bullet.x, enemy.y - bullet.y)
                if dist < enemy.size:
                    if enemy.take_damage(BULLET_DAMAGE):
                        player.kills += 1
                    bullet.alive = False

    # Enemy bullets hit player
    for enemy in enemies:
        for bullet in enemy.bullets:
            dist = math.hypot(player.x - bullet.x, player.y - bullet.y)
            if dist < player.size:
                player.health -= 5
                bullet.alive = False

    # Safe zone shrink
    zone_timer += 1
    if zone_timer > ZONE_SHRINK_INTERVAL and zone_radius > ZONE_MIN_RADIUS:
        zone_radius -= 40
        zone_timer = 0

    # Damage outside zone
    dist_zone = math.hypot(player.x - zone_center[0], player.y - zone_center[1])
    if dist_zone > zone_radius:
        player.health -= ZONE_DAMAGE

    # Draw world
    for tree in trees:
        tree.draw(screen, camera)

    for building in buildings:
        building.draw(screen, camera)

    for item in loot_items:
        item.update()
        item.draw(screen, camera)

    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen, camera)

    # Draw player
    px, py = camera.apply(int(player.x), int(player.y))
    pygame.draw.circle(screen, player.color, (px, py), player.size)

    # Draw bullets
    for b in player.bullets:
        b.draw(screen, camera)

    # Draw safe zone
    zx, zy = camera.apply(zone_center[0], zone_center[1])
    pygame.draw.circle(screen, BLUE, (int(zx), int(zy)), int(zone_radius), 2)

    # UI
    hp_text = font_medium.render(f"HP: {int(player.health)}", True, WHITE)
    ammo_text = font_medium.render(f"Ammo: {player.ammo}/{player.reserve_ammo}", True, WHITE)
    kills_text = font_medium.render(f"Kills: {player.kills}", True, WHITE)
    weapon_text = font_medium.render(f"Gun: {player.weapon}", True, WHITE)

    screen.blit(hp_text, (10, 10))
    screen.blit(ammo_text, (10, 40))
    screen.blit(kills_text, (10, 70))
    screen.blit(weapon_text, (10, 100))

    # Game Over
    if player.health <= 0:
        game_over = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    pygame.display.update()

pygame.quit()
sys.exit()






# ─────────────────────────────────────────────
#  WEAPON SYSTEM
# ─────────────────────────────────────────────
WEAPONS = {
    "Pistol": {
        "damage": 18,
        "bullet_speed": 12,
        "cooldown": 25,
        "mag": 12,
        "reload": 60,
        "recoil": 0.03
    },
    "M416": {
        "damage": 20,
        "bullet_speed": 14,
        "cooldown": 10,
        "mag": 30,
        "reload": 90,
        "recoil": 0.06
    },
    "AKM": {
        "damage": 28,
        "bullet_speed": 15,
        "cooldown": 14,
        "mag": 30,
        "reload": 100,
        "recoil": 0.1
    },
    "Sniper": {
        "damage": 70,
        "bullet_speed": 20,
        "cooldown": 60,
        "mag": 5,
        "reload": 120,
        "recoil": 0.2
    }
}



def shoot(self, target_x, target_y, camera):
    if self.reloading or self.shoot_cooldown > 0 or self.ammo <= 0:
        return

    wx = target_x + camera.offset_x
    wy = target_y + camera.offset_y

    base_angle = math.atan2(wy - self.y, wx - self.x)

    # 🔥 RECOIL (random spray)
    recoil_offset = random.uniform(-self.recoil, self.recoil)
    self.angle = base_angle + recoil_offset

    b = Bullet(self.x, self.y, self.angle, owner="player", damage=self.damage)
    b.speed = self.bullet_speed
    self.bullets.append(b)

    self.ammo -= 1
    self.shoot_cooldown = self.shoot_delay

    # Visual recoil kick (screen feel)
    self.x -= math.cos(self.angle) * 1.5
    self.y -= math.sin(self.angle) * 1.5

    # Muzzle flash
    for _ in range(6):
        self.particles.append(Particle(
            self.x + math.cos(self.angle) * self.size,
            self.y + math.sin(self.angle) * self.size,
            YELLOW, speed=3, lifetime=10, size=3))


if self.reloading:
    self.reload_timer -= 1
    if self.reload_timer <= 0:
        needed = self.max_ammo - self.ammo
        reloaded = min(needed, self.reserve_ammo)
        self.ammo += reloaded
        self.reserve_ammo -= reloaded
        self.reloading = False


if keys[pygame.K_1]:
    self.load_weapon("Pistol")
if keys[pygame.K_2]:
    self.load_weapon("M416")
if keys[pygame.K_3]:
    self.load_weapon("AKM")
if keys[pygame.K_4]:
    self.load_weapon("Sniper")



weapon_text = font_medium.render(f"Gun: {player.weapon}", True, WHITE)
screen.blit(weapon_text, (10, 100))
