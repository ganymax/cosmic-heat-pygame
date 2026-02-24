import sys
import math

import pygame
import random

from controls import move_player, move_player_with_joystick
from classes.constants import WIDTH, HEIGHT, FPS, SHOOT_DELAY
from functions import show_game_over, music_background
from menu import show_menu

from classes.player import Player
from classes.bullets import Bullet
from classes.refill import BulletRefill, HealthRefill, DoubleRefill, ExtraScore
from classes.meteors import Meteors, Meteors2, BlackHole
from classes.explosions import Explosion, Explosion2
from classes.enemies import Enemy1, Enemy2
from classes.bosses import Boss1, Boss2, Boss3


class ParallaxLayer:
    """A single layer of the parallax background with continuous scrolling."""

    def __init__(self, width, height, speed, color_range, star_count, star_size_range):
        self.width = width
        self.height = height
        self.speed = speed
        self.y_offset = 0.0

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._generate_stars(color_range, star_count, star_size_range)

    def _generate_stars(self, color_range, star_count, star_size_range):
        """Generate random stars with varying sizes and colors."""
        for _ in range(star_count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            size = random.randint(star_size_range[0], star_size_range[1])
            brightness = random.randint(color_range[0], color_range[1])

            # Add slight color variation for cosmic feel
            r = min(255, brightness + random.randint(-20, 30))
            g = min(255, brightness + random.randint(-10, 20))
            b = min(255, brightness + random.randint(0, 40))

            if size == 1:
                self.surface.set_at((x, y), (r, g, b, brightness))
            else:
                # Larger stars with glow effect
                glow_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (r, g, b, brightness // 3),
                                   (size * 3 // 2, size * 3 // 2), size * 2)
                pygame.draw.circle(glow_surf, (r, g, b, brightness),
                                   (size * 3 // 2, size * 3 // 2), size)
                self.surface.blit(glow_surf, (x - size, y - size))

    def update(self, dt=1.0):
        """Update the layer's vertical offset for scrolling."""
        self.y_offset += self.speed * dt
        if self.y_offset >= self.height:
            self.y_offset -= self.height

    def draw(self, screen):
        """Draw the layer with seamless vertical wrapping."""
        y1 = int(self.y_offset)
        y2 = y1 - self.height

        screen.blit(self.surface, (0, y1))
        screen.blit(self.surface, (0, y2))


class ParallaxBackground:
    """3-layer parallax background system for cosmic theme."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.base_color = (5, 5, 15)  # Deep space blue-black
        self.nebula_phase = 0.0

        # Layer 1: Distant stars (slowest) - small, dim
        self.layer_far = ParallaxLayer(
            width, height,
            speed=0.3,
            color_range=(80, 150),
            star_count=200,
            star_size_range=(1, 1)
        )

        # Layer 2: Mid-distance stars - medium brightness
        self.layer_mid = ParallaxLayer(
            width, height,
            speed=0.7,
            color_range=(120, 200),
            star_count=100,
            star_size_range=(1, 2)
        )

        # Layer 3: Near stars (fastest) - bright, larger
        self.layer_near = ParallaxLayer(
            width, height,
            speed=1.2,
            color_range=(180, 255),
            star_count=50,
            star_size_range=(2, 3)
        )

        # Pre-render nebula overlay
        self.nebula_surface = self._create_nebula_surface()

    def _create_nebula_surface(self):
        """Create a subtle nebula overlay for cosmic atmosphere."""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(150, 400)

            # Cosmic colors: purples, blues, cyans
            colors = [
                (80, 20, 120, 8),   # Purple
                (20, 40, 100, 6),   # Deep blue
                (20, 80, 100, 5),   # Cyan-blue
                (100, 20, 80, 7),   # Magenta
            ]
            color = random.choice(colors)

            # Create gradient blob
            for r in range(radius, 0, -20):
                alpha = int(color[3] * (r / radius))
                pygame.draw.circle(surface, (*color[:3], alpha), (x, y), r)

        return surface

    def update(self, speed_multiplier=1.0):
        """Update all parallax layers."""
        self.layer_far.update(speed_multiplier)
        self.layer_mid.update(speed_multiplier)
        self.layer_near.update(speed_multiplier)
        self.nebula_phase += 0.01

    def draw(self, screen):
        """Draw the complete parallax background."""
        screen.fill(self.base_color)
        self.layer_far.draw(screen)
        self.layer_mid.draw(screen)

        # Draw nebula with subtle pulsing
        nebula_alpha = int(30 + 10 * math.sin(self.nebula_phase))
        self.nebula_surface.set_alpha(nebula_alpha)
        screen.blit(self.nebula_surface, (0, 0))

        self.layer_near.draw(screen)


class NeonGlowBar:
    """Semi-transparent bar with neon glow effect."""

    def __init__(self, x, y, width, height, icon_image, glow_color, fill_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.icon_image = icon_image
        self.glow_color = glow_color
        self.fill_color = fill_color
        self.low_color = (80, 80, 80)  # Dimmed color when low

        self.icon_width = icon_image.get_width() if icon_image else 0
        self.bar_x_offset = self.icon_width + 5
        self.bar_width = width - self.bar_x_offset

        # Pre-render glow surfaces
        self._create_glow_surfaces()

    def _create_glow_surfaces(self):
        """Create the glow effect surfaces."""
        glow_padding = 6
        glow_width = self.bar_width + glow_padding * 2
        glow_height = self.height + glow_padding * 2

        self.outer_glow = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        self.inner_glow = pygame.Surface((self.bar_width + 4, self.height + 4), pygame.SRCALPHA)

        # Outer glow (softer, larger)
        for i in range(glow_padding, 0, -1):
            alpha = int(40 * (1 - i / glow_padding))
            rect = pygame.Rect(i, i, glow_width - 2 * i, glow_height - 2 * i)
            pygame.draw.rect(self.outer_glow, (*self.glow_color[:3], alpha), rect, border_radius=4)

    def draw(self, screen, current_value, max_value):
        """Draw the neon glow bar with current fill level."""
        fill_ratio = max(0, min(1, current_value / max_value))
        is_low = fill_ratio <= 0.25

        # Create main surface with transparency
        surface = pygame.Surface((self.width, self.height + 12), pygame.SRCALPHA)

        # Draw outer glow
        glow_x = self.bar_x_offset - 6
        glow_y = 0
        if not is_low:
            glow_alpha = int(100 + 30 * math.sin(pygame.time.get_ticks() * 0.005))
            self.outer_glow.set_alpha(glow_alpha)
            surface.blit(self.outer_glow, (glow_x, glow_y))

        # Draw background (semi-transparent dark)
        bar_rect = pygame.Rect(self.bar_x_offset, 6, self.bar_width, self.height)
        pygame.draw.rect(surface, (20, 20, 30, 180), bar_rect, border_radius=3)

        # Draw fill bar
        fill_width = int(self.bar_width * fill_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.bar_x_offset, 6, fill_width, self.height)
            fill_color = self.low_color if is_low else self.fill_color

            # Gradient fill effect
            gradient_surf = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)
            for i in range(self.height):
                brightness = 1.0 - (abs(i - self.height // 2) / self.height) * 0.4
                r = int(fill_color[0] * brightness)
                g = int(fill_color[1] * brightness)
                b = int(fill_color[2] * brightness)
                pygame.draw.line(gradient_surf, (r, g, b, 200), (0, i), (fill_width, i))

            surface.blit(gradient_surf, (self.bar_x_offset, 6))

            # Inner glow on fill bar
            if not is_low:
                inner_glow_surf = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(inner_glow_surf, (*self.glow_color[:3], 60),
                                 (0, 0, fill_width, 3), border_radius=2)
                pygame.draw.rect(inner_glow_surf, (*self.glow_color[:3], 40),
                                 (0, self.height - 3, fill_width, 3), border_radius=2)
                surface.blit(inner_glow_surf, (self.bar_x_offset, 6))

        # Draw border
        border_color = self.glow_color if not is_low else (100, 100, 100)
        pygame.draw.rect(surface, (*border_color, 200), bar_rect, width=2, border_radius=3)

        # Draw icon with glow
        if self.icon_image:
            icon_glow = pygame.Surface((self.icon_width + 8, self.icon_image.get_height() + 8), pygame.SRCALPHA)
            if not is_low:
                glow_alpha = int(60 + 20 * math.sin(pygame.time.get_ticks() * 0.004))
                pygame.draw.rect(icon_glow, (*self.glow_color[:3], glow_alpha),
                                 (0, 0, self.icon_width + 8, self.icon_image.get_height() + 8), border_radius=4)
            surface.blit(icon_glow, (-4, 2))
            surface.blit(self.icon_image, (0, 6))

        screen.blit(surface, (self.x, self.y))


pygame.init()
music_background()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surface = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Heat")
clock = pygame.time.Clock()


explosions = pygame.sprite.Group()
explosions2 = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy1_group = pygame.sprite.Group()
enemy2_group = pygame.sprite.Group()
boss1_group = pygame.sprite.Group()
boss2_group = pygame.sprite.Group()
boss3_group = pygame.sprite.Group()
bullet_refill_group = pygame.sprite.Group()
health_refill_group = pygame.sprite.Group()
double_refill_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
meteor2_group = pygame.sprite.Group()
extra_score_group = pygame.sprite.Group()
black_hole_group = pygame.sprite.Group()
enemy2_bullets = pygame.sprite.Group()

boss1_bullets = pygame.sprite.Group()
boss2_bullets = pygame.sprite.Group()
boss3_bullets = pygame.sprite.Group()

boss1_health = 150
boss1_health_bar_rect = pygame.Rect(0, 0, 150, 5)
boss1_spawned = False

boss2_health = 150
boss2_health_bar_rect = pygame.Rect(0, 0, 150, 5)
boss2_spawned = False

boss3_health = 200
boss3_health_bar_rect = pygame.Rect(0, 0, 200, 5)
boss3_spawned = False

# Initialize parallax background
parallax_bg = ParallaxBackground(WIDTH, HEIGHT)

explosion_images = [pygame.image.load(f"images/explosion/explosion{i}.png") for i in range(8)]
explosion2_images = [pygame.image.load(f"images/explosion2/explosion{i}.png") for i in range(18)]
explosion3_images = [pygame.image.load(f"images/explosion3/explosion{i}.png") for i in range(18)]

enemy1_img = [
    pygame.image.load('images/enemy/enemy1_1.png').convert_alpha(),
    pygame.image.load('images/enemy/enemy1_2.png').convert_alpha(),
    pygame.image.load('images/enemy/enemy1_3.png').convert_alpha()
]
enemy2_img = [
    pygame.image.load('images/enemy/enemy2_1.png').convert_alpha(),
    pygame.image.load('images/enemy/enemy2_2.png').convert_alpha()
]
boss1_img = pygame.image.load('images/boss/boss1.png').convert_alpha()
boss2_img = pygame.image.load('images/boss/boss2_1.png').convert_alpha()
boss3_img = pygame.image.load('images/boss/boss3.png').convert_alpha()

health_refill_img = pygame.image.load('images/refill/health_refill.png').convert_alpha()
bullet_refill_img = pygame.image.load('images/refill/bullet_refill.png').convert_alpha()
double_refill_img = pygame.image.load('images/refill/double_refill.png').convert_alpha()

meteor_imgs = [
    pygame.image.load('images/meteors/meteor_1.png').convert_alpha(),
    pygame.image.load('images/meteors/meteor_2.png').convert_alpha(),
    pygame.image.load('images/meteors/meteor_3.png').convert_alpha(),
    pygame.image.load('images/meteors/meteor_4.png').convert_alpha()
]
meteor2_imgs = [
    pygame.image.load('images/meteors/meteor2_1.png').convert_alpha(),
    pygame.image.load('images/meteors/meteor2_2.png').convert_alpha(),
    pygame.image.load('images/meteors/meteor2_3.png').convert_alpha(),
    pygame.image.load('images/meteors/meteor2_4.png').convert_alpha()
]
extra_score_img = pygame.image.load('images/score/score_coin.png').convert_alpha()
black_hole_imgs = [
    pygame.image.load('images/hole/black_hole.png').convert_alpha(),
    pygame.image.load('images/hole/black_hole2.png').convert_alpha()
]

# Load UI icons
life_bar_icon = pygame.image.load("images/life_bar.png").convert_alpha()
bullet_bar_icon = pygame.image.load("images/bullet_bar.png").convert_alpha()

# Create neon glow bars
health_bar = NeonGlowBar(
    x=10, y=10,
    width=200, height=20,
    icon_image=life_bar_icon,
    glow_color=(0, 255, 150),      # Cyan-green glow
    fill_color=(80, 220, 140)       # Green fill
)

ammo_bar = NeonGlowBar(
    x=10, y=50,
    width=200, height=20,
    icon_image=bullet_bar_icon,
    glow_color=(255, 80, 80),       # Red glow
    fill_color=(220, 80, 80)        # Red fill
)

initial_player_pos = (WIDTH // 2, HEIGHT - 100)

score = 0
hi_score = 0
player = Player()
player_life = 200
bullet_counter = 200

paused = False
running = True

joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

if show_menu:
    import menu
    menu.main()

is_shooting = False
last_shot_time = 0


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not paused:
                if bullet_counter > 0 and pygame.time.get_ticks() - last_shot_time > SHOOT_DELAY:
                    last_shot_time = pygame.time.get_ticks()
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullets.add(bullet)
                    bullet_counter -= 1
                is_shooting = True

            elif event.key == pygame.K_ESCAPE:
                sys.exit(0)
            elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                paused = not paused
            elif not paused:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()
                elif event.key == pygame.K_UP:
                    player.move_up()
                elif event.key == pygame.K_DOWN:
                    player.move_down()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and player.original_image is not None:
                player.image = player.original_image.copy()
                is_shooting = False
            elif not paused:
                if event.key == pygame.K_LEFT:
                    player.stop_left()
                elif event.key == pygame.K_RIGHT:
                    player.stop_right()
                elif event.key == pygame.K_UP:
                    player.stop_up()
                elif event.key == pygame.K_DOWN:
                    player.stop_down()

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0 and not paused:
                is_shooting = True
                if bullet_counter > 0:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullets.add(bullet)
                    bullet_counter -= 1
            elif event.button == 7:
                paused = not paused
        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 0 and player.original_image is not None:
                is_shooting = False

    if pygame.time.get_ticks() - last_shot_time > SHOOT_DELAY and is_shooting and not paused:
        if bullet_counter > 0:
            last_shot_time = pygame.time.get_ticks()
            bullet = Bullet(player.rect.centerx, player.rect.top)
            bullets.add(bullet)
            bullet_counter -= 1

    if joystick:
        if not paused:
            move_player_with_joystick(joystick, player)

    if paused:
        font = pygame.font.SysFont('Comic Sans MS', 40)
        text = font.render("PAUSE", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()

    if not paused:
        move_player(keys, player)

    # Calculate parallax speed multiplier based on score
    speed_mult = 1.0
    if score > 3000:
        speed_mult = 1.5
    if score > 10000:
        speed_mult = 2.0
    if score > 15000:
        speed_mult = 2.5

    # Update and draw parallax background
    parallax_bg.update(speed_mult)
    parallax_bg.draw(screen)

    if score > hi_score:
        hi_score = score

    if random.randint(0, 120) == 0:
        enemy_img = random.choice(enemy1_img)
        enemy_object = Enemy1(
            random.randint(100, WIDTH - 50),
            random.randint(-HEIGHT, -50),
            enemy_img,
        )
        enemy1_group.add(enemy_object)

    if score >= 3000 and random.randint(0, 40) == 0 and len(enemy2_group) < 2:
        enemy_img = random.choice(enemy2_img)
        enemy2_object = Enemy2(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            enemy_img,
        )
        enemy2_group.add(enemy2_object)

    if score >= 5000 and not boss1_spawned:
        pygame.mixer.Sound('game_sounds/warning.mp3').play()
        boss1_img = boss1_img
        boss1_object = Boss1(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss1_img,
        )
        boss1_group.add(boss1_object)
        boss1_spawned = True

    if score >= 10000 and not boss2_spawned:
        pygame.mixer.Sound('game_sounds/warning.mp3').play()
        boss2_img = boss2_img
        boss2_object = Boss2(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss2_img,
        )
        boss2_group.add(boss2_object)
        boss2_spawned = True

    if score >= 15000 and not boss3_spawned:
        pygame.mixer.Sound('game_sounds/warning.mp3').play()
        boss3_img = boss3_img
        boss3_object = Boss3(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss3_img,
        )
        boss3_group.add(boss3_object)
        boss3_spawned = True

    if random.randint(0, 60) == 0:
        extra_score = ExtraScore(
            random.randint(50, WIDTH - 50),
            random.randint(-HEIGHT, -50 - extra_score_img.get_rect().height),
            extra_score_img,
        )

        extra_score_group.add(extra_score)

    if score > 3000 and random.randint(0, 100) == 0:
        meteor_img = random.choice(meteor_imgs)
        meteor_object = Meteors(
            random.randint(0, 50),
            random.randint(0, 50),
            meteor_img,
        )
        meteor_group.add(meteor_object)

    if random.randint(0, 90) == 0:
        meteor2_img = random.choice(meteor2_imgs)
        meteor2_object = Meteors2(
            random.randint(100, WIDTH - 50),
            random.randint(-HEIGHT, -50 - meteor2_img.get_rect().height),
            meteor2_img,
        )
        meteor2_group.add(meteor2_object)

    if score > 1000 and random.randint(0, 500) == 0:
        black_hole_img = random.choice(black_hole_imgs)
        black_hole_object = BlackHole(
            random.randint(100, WIDTH - 50),
            random.randint(-HEIGHT, -50 - black_hole_img.get_rect().height),
            black_hole_img,
        )
        black_hole_group.add(black_hole_object)

    if player_life <= 0:
        show_game_over(score)
        boss1_spawned = False
        boss1_health = 150
        boss2_spawned = False
        boss2_health = 150
        boss3_spawned = False
        boss3_health = 200
        score = 0
        player_life = 200
        bullet_counter = 200
        player.rect.topleft = initial_player_pos
        bullets.empty()
        bullet_refill_group.empty()
        health_refill_group.empty()
        double_refill_group.empty()
        extra_score_group.empty()
        black_hole_group.empty()
        meteor_group.empty()
        meteor2_group.empty()
        enemy1_group.empty()
        enemy2_group.empty()
        boss1_group.empty()
        boss2_group.empty()
        boss3_group.empty()
        explosions.empty()
        explosions2.empty()

    for black_hole_object in black_hole_group:
        black_hole_object.update()
        black_hole_object.draw(screen)

        if black_hole_object.rect.colliderect(player.rect):
            player_life -= 1
            black_hole_object.sound_effect.play()

        if score >= 5000:
            meteor_object.speed = 4
        if score >= 10000:
            meteor_object.speed = 4
        if score >= 15000:
            meteor_object.speed = 6
        if score >= 20000:
            meteor_object.speed = 8

    for bullet_refill in bullet_refill_group:

        bullet_refill.update()
        bullet_refill.draw(screen)

        if player.rect.colliderect(bullet_refill.rect):
            if bullet_counter < 200:
                bullet_counter += 50
                if bullet_counter > 200:
                    bullet_counter = 200
                bullet_refill.kill()
                bullet_refill.sound_effect.play()
            else:
                bullet_refill.kill()
                bullet_refill.sound_effect.play()

    for health_refill in health_refill_group:
        health_refill.update()
        health_refill.draw(screen)

        if player.rect.colliderect(health_refill.rect):
            if player_life < 200:
                player_life += 50
                if player_life > 200:
                    player_life = 200
                health_refill.kill()
                health_refill.sound_effect.play()
            else:
                health_refill.kill()
                health_refill.sound_effect.play()

    for extra_score in extra_score_group:
        extra_score.update()
        extra_score.draw(screen)

        if player.rect.colliderect(extra_score.rect):
            score += 20
            extra_score.kill()
            extra_score.sound_effect.play()

        if score >= 3000:
            extra_score.speed = 2
        if score >= 10000:
            extra_score.speed = 4
        if score >= 15000:
            extra_score.speed = 6
        if score >= 20000:
            extra_score.speed = 8

    for double_refill in double_refill_group:
        double_refill.update()
        double_refill.draw(screen)

        if player.rect.colliderect(double_refill.rect):
            if player_life < 200:
                player_life += 50
                if player_life > 200:
                    player_life = 200
            if bullet_counter < 200:
                bullet_counter += 50
                if bullet_counter > 200:
                    bullet_counter = 200
                double_refill.kill()
                double_refill.sound_effect.play()
            else:
                double_refill.kill()
                double_refill.sound_effect.play()

    for meteor_object in meteor_group:
        meteor_object.update()
        meteor_object.draw(screen)

        if meteor_object.rect.colliderect(player.rect):
            player_life -= 10
            explosion = Explosion(meteor_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor_object.kill()
            score += 50

        bullet_collisions = pygame.sprite.spritecollide(meteor_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion = Explosion(meteor_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor_object.kill()
            score += 80

            if random.randint(0, 10) == 0:
                double_refill = DoubleRefill(
                    meteor_object.rect.centerx,
                    meteor_object.rect.centery,
                    double_refill_img,
                )
                double_refill_group.add(double_refill)

        if score >= 3000:
            meteor_object.speed = 4
        if score >= 10000:
            meteor_object.speed = 6
        if score >= 15000:
            meteor_object.speed = 8
        if score >= 20000:
            meteor_object.speed = 10

    for meteor2_object in meteor2_group:
        meteor2_object.update()
        meteor2_object.draw(screen)

        if meteor2_object.rect.colliderect(player.rect):
            player_life -= 10
            explosion = Explosion(meteor2_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor2_object.kill()
            score += 20

        bullet_collisions = pygame.sprite.spritecollide(meteor2_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion = Explosion(meteor2_object.rect.center, explosion_images)
            explosions.add(explosion)
            meteor2_object.kill()
            score += 40

            if random.randint(0, 20) == 0:
                double_refill = DoubleRefill(
                    meteor2_object.rect.centerx,
                    meteor2_object.rect.centery,
                    double_refill_img,
                )
                double_refill_group.add(double_refill)

        if score >= 3000:
            meteor2_object.speed = 4
        if score >= 10000:
            meteor2_object.speed = 6
        if score >= 15000:
            meteor2_object.speed = 8
        if score >= 20000:
            meteor2_object.speed = 10

    for enemy_object in enemy1_group:
        enemy_object.update(enemy1_group)
        enemy1_group.draw(screen)

        if enemy_object.rect.colliderect(player.rect):
            player_life -= 10
            explosion = Explosion(enemy_object.rect.center, explosion_images)
            explosions.add(explosion)
            enemy_object.kill()
            score += 20

        bullet_collisions = pygame.sprite.spritecollide(enemy_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion = Explosion(enemy_object.rect.center, explosion_images)
            explosions.add(explosion)
            enemy_object.kill()
            score += 50

            if random.randint(0, 8) == 0:
                bullet_refill = BulletRefill(
                    enemy_object.rect.centerx,
                    enemy_object.rect.centery,
                    bullet_refill_img,
                )
                bullet_refill_group.add(bullet_refill)

            if random.randint(0, 8) == 0:
                health_refill = HealthRefill(
                    random.randint(50, WIDTH - 30),
                    random.randint(-HEIGHT, -30),
                    health_refill_img,
                )
                health_refill_group.add(health_refill)

    for enemy2_object in enemy2_group:
        enemy2_object.update(enemy2_group, enemy2_bullets, player)
        enemy2_group.draw(screen)
        enemy2_bullets.update()
        enemy2_bullets.draw(screen)

        if enemy2_object.rect.colliderect(player.rect):
            player_life -= 40
            explosion2 = Explosion2(enemy2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            enemy2_object.kill()
            score += 20

        bullet_collisions = pygame.sprite.spritecollide(enemy2_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion2(enemy2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            enemy2_object.kill()
            score += 80

            if random.randint(0, 20) == 0:
                double_refill = DoubleRefill(
                    enemy2_object.rect.centerx,
                    enemy2_object.rect.centery,
                    double_refill_img,
                )
                double_refill_group.add(double_refill)

        for enemy2_bullet in enemy2_bullets:
            if enemy2_bullet.rect.colliderect(player.rect):
                player_life -= 10
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                enemy2_bullet.kill()

    for boss1_object in boss1_group:
        boss1_object.update(boss1_bullets, player)
        boss1_group.draw(screen)
        boss1_bullets.update()
        boss1_bullets.draw(screen)

        if boss1_object.rect.colliderect(player.rect):
            player_life -= 20
            explosion = Explosion2(boss1_object.rect.center, explosion2_images)
            explosions2.add(explosion)

        bullet_collisions = pygame.sprite.spritecollide(boss1_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion(boss1_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            boss1_health -= 5
            if boss1_health <= 0:
                explosion = Explosion2(boss1_object.rect.center, explosion3_images)
                explosions.add(explosion)
                boss1_object.kill()
                score += 400

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        boss1_object.rect.centerx,
                        boss1_object.rect.centery,
                        double_refill_img,
                    )
                    double_refill_group.add(double_refill)

        for boss1_bullet in boss1_bullets:
            if boss1_bullet.rect.colliderect(player.rect):
                player_life -= 20
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                boss1_bullet.kill()

        if boss1_health <= 0:
            explosion = Explosion2(boss1_object.rect.center, explosion2_images)
            explosions2.add(explosion)
            boss1_object.kill()

    if boss1_group:
        boss1_object = boss1_group.sprites()[0]
        boss1_health_bar_rect.center = (boss1_object.rect.centerx, boss1_object.rect.top - 5)
        pygame.draw.rect(screen, (255, 0, 0), boss1_health_bar_rect)
        pygame.draw.rect(screen, (0, 255, 0), (boss1_health_bar_rect.left, boss1_health_bar_rect.top, boss1_health, boss1_health_bar_rect.height))

    for boss2_object in boss2_group:
        boss2_object.update(boss2_bullets, player)
        boss2_group.draw(screen)
        boss2_bullets.update()
        boss2_bullets.draw(screen)

        if boss2_object.rect.colliderect(player.rect):
            player_life -= 2
            explosion2 = Explosion2(boss2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)

        bullet_collisions = pygame.sprite.spritecollide(boss2_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion2(boss2_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            boss2_health -= 8
            if boss2_health <= 0:
                explosion2 = Explosion2(boss2_object.rect.center, explosion3_images)
                explosions2.add(explosion2)
                boss2_object.kill()
                score += 800

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        boss2_object.rect.centerx,
                        boss2_object.rect.centery,
                        double_refill_img,
                    )
                    double_refill_group.add(double_refill)

        for boss2_bullet in boss2_bullets:
            if boss2_bullet.rect.colliderect(player.rect):
                player_life -= 20
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                boss2_bullet.kill()

        if boss2_health <= 0:
            explosion = Explosion2(boss2_object.rect.center, explosion2_images)
            explosions2.add(explosion)
            boss2_object.kill()

    if boss2_group:
        boss2_object = boss2_group.sprites()[0]
        boss2_health_bar_rect.center = (boss2_object.rect.centerx, boss2_object.rect.top - 5)
        pygame.draw.rect(screen, (255, 0, 0), boss2_health_bar_rect)
        pygame.draw.rect(screen, (0, 255, 0), (boss2_health_bar_rect.left, boss2_health_bar_rect.top, boss2_health, boss2_health_bar_rect.height))

    for boss3_object in boss3_group:
        boss3_object.update(boss3_bullets, player)
        boss3_group.draw(screen)
        boss3_bullets.update()
        boss3_bullets.draw(screen)

        if boss3_object.rect.colliderect(player.rect):
            player_life -= 1
            explosion2 = Explosion2(boss3_object.rect.center, explosion2_images)
            explosions2.add(explosion2)

        bullet_collisions = pygame.sprite.spritecollide(boss3_object, bullets, True)
        for bullet_collision in bullet_collisions:
            explosion2 = Explosion2(boss3_object.rect.center, explosion2_images)
            explosions2.add(explosion2)
            boss3_health -= 6
            if boss3_health <= 0:
                explosion2 = Explosion2(boss3_object.rect.center, explosion3_images)
                explosions2.add(explosion2)
                boss3_object.kill()
                score += 1000

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        boss3_object.rect.centerx,
                        boss3_object.rect.centery,
                        double_refill_img,
                    )
                    double_refill_group.add(double_refill)

        for boss3_bullet in boss3_bullets:
            if boss3_bullet.rect.colliderect(player.rect):
                player_life -= 20
                explosion = Explosion(player.rect.center, explosion3_images)
                explosions.add(explosion)
                boss3_bullet.kill()

        if boss3_health <= 0:
            explosion = Explosion2(boss3_object.rect.center, explosion2_images)
            explosions2.add(explosion)
            boss3_object.kill()

    if boss3_group:
        boss3_object = boss3_group.sprites()[0]
        boss3_health_bar_rect.center = (
            boss3_object.rect.centerx,
            boss3_object.rect.top - 5
        )
        pygame.draw.rect(screen, (255, 0, 0), boss3_health_bar_rect)
        pygame.draw.rect(screen, (0, 255, 0), (
            boss3_health_bar_rect.left,
            boss3_health_bar_rect.top,
            boss3_health,
            boss3_health_bar_rect.height)
        )

    player_image_copy = player.image.copy()
    screen.blit(player_image_copy, player.rect)

    for explosion in explosions:
        explosion.update()
        screen.blit(explosion.image, explosion.rect)

    for explosion2 in explosions2:
        explosion2.update()
        screen.blit(explosion2.image, explosion2.rect)

    for bullet in bullets:
        bullet.update()
        screen.blit(bullet.image, bullet.rect)

        if bullet.rect.bottom < 0:
            bullet.kill()
            bullet_counter -= 1

    # Draw neon glow UI bars
    health_bar.draw(screen, player_life, 200)
    ammo_bar.draw(screen, bullet_counter, 200)

    # Draw score with neon glow effect
    score_font = pygame.font.SysFont('Arial', 30, bold=True)
    score_text = f'{score}'
    score_surface = score_font.render(score_text, True, (255, 220, 100))

    # Create glow for score
    glow_surface = pygame.Surface((score_surface.get_width() + 20, score_surface.get_height() + 20), pygame.SRCALPHA)
    glow_text = score_font.render(score_text, True, (255, 180, 50))
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        glow_surface.blit(glow_text, (10 + offset[0], 10 + offset[1]))
    glow_surface.set_alpha(80)

    score_x = WIDTH - score_surface.get_width() - extra_score_img.get_width() - 20
    screen.blit(glow_surface, (score_x - 10, 5))
    screen.blit(score_surface, (score_x, 10))
    screen.blit(extra_score_img, (score_x + score_surface.get_width() + 5, 10))

    # Draw hi-score with subtle glow
    hi_score_font = pygame.font.SysFont('Arial', 20)
    hi_score_surface = hi_score_font.render(f'HI-SCORE: {hi_score}', True, (200, 200, 255))
    hi_score_surface.set_alpha(180)
    hi_score_x_pos = (screen.get_width() - hi_score_surface.get_width()) // 2
    screen.blit(hi_score_surface, (hi_score_x_pos, 5))

    pygame.display.flip()

    clock.tick(FPS)

pygame.mixer.music.stop()
pygame.quit()
sys.exit()
