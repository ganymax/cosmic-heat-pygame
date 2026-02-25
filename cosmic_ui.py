"""
Modern cosmic theme UI components for Cosmic Heat.
Provides parallax background system and neon-styled UI elements.
"""

import pygame
import random
import math
from classes.constants import WIDTH, HEIGHT


class ParallaxLayer:
    """A single scrolling layer in the parallax background system."""
    
    def __init__(self, speed, star_count, star_size_range, color_palette, alpha=255):
        self.speed = speed
        self.y_offset = 0.0
        self.surface = pygame.Surface((WIDTH, HEIGHT * 2), pygame.SRCALPHA)
        self._generate_stars(star_count, star_size_range, color_palette, alpha)
    
    def _generate_stars(self, count, size_range, colors, alpha):
        """Generate procedural stars for this layer."""
        for _ in range(count):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT * 2)
            size = random.randint(size_range[0], size_range[1])
            color = random.choice(colors)
            if len(color) == 3:
                color = (*color, alpha)
            
            if size <= 2:
                pygame.draw.circle(self.surface, color, (x, y), size)
            else:
                self._draw_star_glow(x, y, size, color)
    
    def _draw_star_glow(self, x, y, size, color):
        """Draw a star with a soft glow effect."""
        base_color = color[:3]
        for i in range(size, 0, -1):
            alpha = int((1 - i / size) * color[3] * 0.6)
            glow_color = (*base_color, alpha)
            pygame.draw.circle(self.surface, glow_color, (x, y), i)
        pygame.draw.circle(self.surface, color, (x, y), max(1, size // 3))
    
    def update(self, dt=1):
        """Update layer position for continuous scrolling."""
        self.y_offset += self.speed * dt
        if self.y_offset >= HEIGHT:
            self.y_offset -= HEIGHT
    
    def draw(self, screen):
        """Draw the layer with seamless vertical wrapping."""
        y = int(self.y_offset)
        screen.blit(self.surface, (0, y - HEIGHT))
        screen.blit(self.surface, (0, y))


class NebulaLayer:
    """Procedural nebula clouds for atmospheric depth."""
    
    def __init__(self, speed, cloud_count=8):
        self.speed = speed
        self.y_offset = 0.0
        self.surface = pygame.Surface((WIDTH, HEIGHT * 2), pygame.SRCALPHA)
        self._generate_nebula(cloud_count)
    
    def _generate_nebula(self, count):
        """Generate soft nebula cloud patches."""
        nebula_colors = [
            (138, 43, 226),   # Blue violet
            (75, 0, 130),     # Indigo
            (0, 100, 150),    # Deep teal
            (150, 0, 100),    # Magenta
            (30, 60, 120),    # Deep blue
        ]
        
        for _ in range(count):
            x = random.randint(-100, WIDTH + 100)
            y = random.randint(0, HEIGHT * 2)
            base_color = random.choice(nebula_colors)
            size = random.randint(150, 400)
            
            for r in range(size, 0, -10):
                alpha = int(8 * (1 - r / size))
                color = (*base_color, alpha)
                pygame.draw.circle(self.surface, color, (x, y), r)
    
    def update(self, dt=1):
        self.y_offset += self.speed * dt
        if self.y_offset >= HEIGHT:
            self.y_offset -= HEIGHT
    
    def draw(self, screen):
        y = int(self.y_offset)
        screen.blit(self.surface, (0, y - HEIGHT))
        screen.blit(self.surface, (0, y))


class ParallaxBackground:
    """
    Three-layer parallax background system.
    Layer 1 (far): Distant small stars - slowest
    Layer 2 (mid): Nebula clouds and medium stars
    Layer 3 (near): Bright stars - fastest
    """
    
    def __init__(self):
        self.base_color = (5, 5, 15)
        
        # Far layer - tiny distant stars
        far_colors = [
            (100, 100, 120),
            (80, 80, 100),
            (120, 110, 130),
        ]
        self.far_layer = ParallaxLayer(
            speed=0.3,
            star_count=200,
            star_size_range=(1, 1),
            color_palette=far_colors,
            alpha=180
        )
        
        # Nebula layer - atmospheric clouds
        self.nebula_layer = NebulaLayer(speed=0.5, cloud_count=10)
        
        # Mid layer - medium stars
        mid_colors = [
            (180, 180, 220),
            (200, 200, 255),
            (255, 220, 180),
            (180, 220, 255),
        ]
        self.mid_layer = ParallaxLayer(
            speed=0.8,
            star_count=100,
            star_size_range=(1, 3),
            color_palette=mid_colors,
            alpha=220
        )
        
        # Near layer - bright prominent stars
        near_colors = [
            (255, 255, 255),
            (255, 240, 220),
            (220, 240, 255),
            (255, 200, 150),
        ]
        self.near_layer = ParallaxLayer(
            speed=1.5,
            star_count=40,
            star_size_range=(2, 5),
            color_palette=near_colors,
            alpha=255
        )
    
    def update(self, speed_multiplier=1.0):
        """Update all layers. speed_multiplier allows game-state speed changes."""
        self.far_layer.update(speed_multiplier)
        self.nebula_layer.update(speed_multiplier)
        self.mid_layer.update(speed_multiplier)
        self.near_layer.update(speed_multiplier)
    
    def draw(self, screen):
        """Draw all layers from back to front."""
        screen.fill(self.base_color)
        self.far_layer.draw(screen)
        self.nebula_layer.draw(screen)
        self.mid_layer.draw(screen)
        self.near_layer.draw(screen)


class NeonBar:
    """Semi-transparent bar with neon glow effect for health/ammo display."""
    
    def __init__(self, x, y, width, height, icon_surface, 
                 fill_color, glow_color, low_threshold=0.25):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.icon = icon_surface
        self.fill_color = fill_color
        self.glow_color = glow_color
        self.low_threshold = low_threshold
        self.low_color = (200, 30, 30)
        self.low_glow = (255, 50, 50)
        
        self.icon_padding = 8
        self.bar_x_offset = self.icon.get_width() + self.icon_padding if icon_surface else 0
        self.bar_width = width - self.bar_x_offset - 5
        
        self.glow_surface = pygame.Surface(
            (self.bar_width + 20, height + 20), pygame.SRCALPHA
        )
        self.pulse_time = 0
    
    def draw(self, screen, current_value, max_value):
        """Draw the neon bar with current fill level."""
        ratio = max(0, min(1, current_value / max_value))
        is_low = ratio <= self.low_threshold
        
        # Pulse effect when low
        self.pulse_time += 0.15
        pulse = 0.7 + 0.3 * math.sin(self.pulse_time) if is_low else 1.0
        
        active_fill = self.low_color if is_low else self.fill_color
        active_glow = self.low_glow if is_low else self.glow_color
        
        # Background panel (semi-transparent dark)
        panel = pygame.Surface((self.width, self.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(
            panel, (10, 10, 20, 180),
            (0, 0, self.width, self.height + 4),
            border_radius=6
        )
        pygame.draw.rect(
            panel, (*active_glow[:3], 60),
            (0, 0, self.width, self.height + 4),
            width=1, border_radius=6
        )
        screen.blit(panel, (self.x, self.y))
        
        # Draw icon
        if self.icon:
            icon_y = self.y + (self.height - self.icon.get_height()) // 2 + 2
            screen.blit(self.icon, (self.x + 4, icon_y))
        
        # Glow effect
        self.glow_surface.fill((0, 0, 0, 0))
        fill_width = int(self.bar_width * ratio)
        if fill_width > 0:
            glow_alpha = int(80 * pulse)
            for i in range(3, 0, -1):
                glow_rect = pygame.Rect(
                    10 - i * 2, 10 - i * 2,
                    fill_width + i * 4, self.height + i * 4
                )
                glow_col = (*active_glow[:3], glow_alpha // (i + 1))
                pygame.draw.rect(self.glow_surface, glow_col, glow_rect, border_radius=4)
            
            screen.blit(
                self.glow_surface,
                (self.x + self.bar_x_offset - 10, self.y - 8)
            )
        
        # Main bar fill
        bar_rect = pygame.Rect(
            self.x + self.bar_x_offset,
            self.y + 2,
            fill_width,
            self.height
        )
        if fill_width > 0:
            fill_alpha = int(200 * pulse)
            bar_surface = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)
            
            # Gradient fill
            for i in range(self.height):
                gradient_factor = 1 - (abs(i - self.height // 2) / (self.height // 2)) * 0.3
                col = tuple(int(c * gradient_factor) for c in active_fill[:3])
                pygame.draw.line(bar_surface, (*col, fill_alpha), (0, i), (fill_width, i))
            
            screen.blit(bar_surface, bar_rect.topleft)
            
            # Bright edge highlight
            highlight_rect = pygame.Rect(0, 0, fill_width, 2)
            pygame.draw.rect(bar_surface, (*active_glow[:3], 150), highlight_rect)
            screen.blit(bar_surface, bar_rect.topleft)
        
        # Bar border
        border_rect = pygame.Rect(
            self.x + self.bar_x_offset - 1,
            self.y + 1,
            self.bar_width + 2,
            self.height + 2
        )
        pygame.draw.rect(
            screen, (*active_glow[:3], int(120 * pulse)),
            border_rect, width=1, border_radius=3
        )


class CosmicScoreDisplay:
    """Neon-styled score display."""
    
    def __init__(self, x, y, score_icon):
        self.x = x
        self.y = y
        self.icon = score_icon
        self.font = pygame.font.SysFont('Arial', 28, bold=True)
        self.glow_color = (255, 215, 0)
    
    def draw(self, screen, score, right_align=True):
        """Draw the score with neon glow effect."""
        text = self.font.render(f'{score:,}', True, (255, 255, 240))
        text_width = text.get_width()
        icon_width = self.icon.get_width()
        total_width = text_width + icon_width + 10
        
        if right_align:
            base_x = self.x - total_width
        else:
            base_x = self.x
        
        # Panel background
        panel = pygame.Surface((total_width + 20, 40), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 10, 20, 160), (0, 0, total_width + 20, 40), border_radius=8)
        pygame.draw.rect(panel, (*self.glow_color, 40), (0, 0, total_width + 20, 40), width=1, border_radius=8)
        screen.blit(panel, (base_x - 10, self.y - 5))
        
        # Glow behind text
        glow_surf = pygame.Surface((text_width + 10, 30), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*self.glow_color, 30), (0, 0, text_width + 10, 30), border_radius=4)
        screen.blit(glow_surf, (base_x - 5, self.y))
        
        screen.blit(text, (base_x, self.y + 2))
        screen.blit(self.icon, (base_x + text_width + 8, self.y + 5))


class CosmicHiScoreDisplay:
    """Semi-transparent hi-score display for top center of screen."""
    
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 18)
    
    def draw(self, screen, hi_score):
        text = self.font.render(f'HI-SCORE: {hi_score:,}', True, (200, 200, 220))
        text_rect = text.get_rect(centerx=WIDTH // 2, top=8)
        
        # Subtle background
        bg = pygame.Surface((text_rect.width + 30, text_rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(bg, (20, 20, 40, 100), (0, 0, bg.get_width(), bg.get_height()), border_radius=5)
        screen.blit(bg, (text_rect.x - 15, text_rect.y - 5))
        
        screen.blit(text, text_rect)


class NeonButton:
    """Neon-styled button with glow effect that intensifies when selected."""
    
    def __init__(self, x, y, width, height, text, 
                 base_color=(100, 150, 255), glow_color=(150, 200, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.glow_color = glow_color
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        self.pulse_time = 0
    
    def draw(self, screen, selected=False):
        """Draw button with varying glow intensity based on selection state."""
        self.pulse_time += 0.1
        
        if selected:
            pulse = 0.7 + 0.3 * math.sin(self.pulse_time * 2)
            glow_intensity = 1.0
            glow_layers = 5
        else:
            pulse = 1.0
            glow_intensity = 0.3
            glow_layers = 2
        
        # Outer glow layers
        for i in range(glow_layers, 0, -1):
            glow_rect = self.rect.inflate(i * 8, i * 6)
            glow_alpha = int(40 * glow_intensity * pulse / i)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surface, 
                (*self.glow_color, glow_alpha),
                (0, 0, glow_rect.width, glow_rect.height),
                border_radius=12
            )
            screen.blit(glow_surface, glow_rect.topleft)
        
        # Button background
        bg_alpha = int(180 * pulse) if selected else 140
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface,
            (15, 20, 40, bg_alpha),
            (0, 0, self.rect.width, self.rect.height),
            border_radius=10
        )
        screen.blit(bg_surface, self.rect.topleft)
        
        # Border with glow
        border_alpha = int(200 * pulse) if selected else 80
        border_width = 3 if selected else 1
        pygame.draw.rect(
            screen,
            (*self.glow_color, border_alpha),
            self.rect,
            width=border_width,
            border_radius=10
        )
        
        # Inner highlight line at top
        if selected:
            highlight_rect = pygame.Rect(
                self.rect.x + 10, self.rect.y + 2,
                self.rect.width - 20, 2
            )
            highlight_surface = pygame.Surface((highlight_rect.width, 2), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (*self.glow_color, int(150 * pulse)), 
                           (0, 0, highlight_rect.width, 2), border_radius=1)
            screen.blit(highlight_surface, highlight_rect.topleft)
        
        # Text with glow when selected
        text_color = (255, 255, 255) if selected else (200, 200, 220)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        if selected:
            # Text glow
            glow_text = self.font.render(self.text, True, self.glow_color)
            for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                screen.blit(glow_text, (text_rect.x + offset[0], text_rect.y + offset[1]))
        
        screen.blit(text_surface, text_rect)
    
    def collidepoint(self, pos):
        """Check if a point is within the button."""
        return self.rect.collidepoint(pos)
