import pygame
from classes.constants import WIDTH, HEIGHT
from cosmic_ui import ParallaxBackground

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def music_background():
    pygame.mixer.music.load('game_sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(loops=-1)


def show_game_over(score):
    parallax_bg = ParallaxBackground()
    font = pygame.font.SysFont('Impact', 50)
    font_small = pygame.font.SysFont('Impact', 30)
    
    pygame.mixer.music.load('game_sounds/gameover.mp3')
    pygame.mixer.music.play()
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = 4000
    
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        parallax_bg.update(0.3)
        parallax_bg.draw(screen)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Game over text with glow
        text = font.render("GAME OVER", True, (255, 50, 50))
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        
        # Glow effect
        glow_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 50, 50, 30), 
                        (0, 0, glow_surface.get_width(), glow_surface.get_height()), 
                        border_radius=10)
        screen.blit(glow_surface, (text_rect.x - 20, text_rect.y - 10))
        screen.blit(text, text_rect)
        
        # Score text
        score_text = font_small.render(f"Final Score: {score:,}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
        screen.blit(score_text, score_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    music_background()


def show_game_win():
    parallax_bg = ParallaxBackground()
    font = pygame.font.SysFont('Impact', 50)
    
    pygame.mixer.music.load('game_sounds/win.mp3')
    pygame.mixer.music.play()
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = 1000
    
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        parallax_bg.update(1.5)
        parallax_bg.draw(screen)
        
        # Win text with glow
        text = font.render("AWESOME! GO ON!", True, (100, 255, 150))
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        # Glow effect
        glow_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (100, 255, 150, 40), 
                        (0, 0, glow_surface.get_width(), glow_surface.get_height()), 
                        border_radius=10)
        screen.blit(glow_surface, (text_rect.x - 20, text_rect.y - 10))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    music_background()
