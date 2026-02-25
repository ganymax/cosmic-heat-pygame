import pygame
from classes.constants import WIDTH, HEIGHT, FPS
from cosmic_ui import ParallaxBackground, NeonText

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def music_background():
    pygame.mixer.music.load('game_sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(loops=-1)


def show_game_over(score):
    """Display game over screen with animated parallax background and neon text."""
    clock = pygame.time.Clock()
    parallax_bg = ParallaxBackground()
    title_text = NeonText(font_size=60, bold=True)
    score_text = NeonText(font_size=32, bold=True)
    
    pygame.mixer.music.load('game_sounds/gameover.mp3')
    pygame.mixer.music.play()
    
    start_time = pygame.time.get_ticks()
    duration = 4000
    
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        parallax_bg.update(0.3)
        parallax_bg.draw(screen)
        
        title_text.draw(
            screen, "GAME OVER",
            (WIDTH // 2, HEIGHT // 2 - 50),
            color=(255, 60, 60),
            glow_color=(255, 100, 100),
            pulse=True
        )
        
        score_text.draw(
            screen, f"Final Score: {score:,}",
            (WIDTH // 2, HEIGHT // 2 + 50),
            color=(255, 255, 255),
            glow_color=(200, 200, 255),
            pulse=False
        )
        
        pygame.display.flip()
        clock.tick(FPS)
    
    music_background()


def show_game_win():
    """Display win screen with animated parallax background and neon text."""
    clock = pygame.time.Clock()
    parallax_bg = ParallaxBackground()
    title_text = NeonText(font_size=50, bold=True)
    
    pygame.mixer.music.load('game_sounds/win.mp3')
    pygame.mixer.music.play()
    
    start_time = pygame.time.get_ticks()
    duration = 1000
    
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        parallax_bg.update(1.5)
        parallax_bg.draw(screen)
        
        title_text.draw(
            screen, "AWESOME! GO ON!",
            (WIDTH // 2, HEIGHT // 2),
            color=(100, 255, 150),
            glow_color=(150, 255, 200),
            pulse=True
        )
        
        pygame.display.flip()
        clock.tick(FPS)
    
    music_background()
