import sys
import pygame
from classes.constants import WIDTH, HEIGHT, FPS
from cosmic_ui import ParallaxBackground, NeonText, NeonButton

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def music_background():
    pygame.mixer.music.load('game_sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(loops=-1)


def show_game_over(score):
    """
    Display interactive game over screen with Retry and Exit buttons.
    Returns: 'retry' to restart the game, 'exit' to quit
    """
    clock = pygame.time.Clock()
    parallax_bg = ParallaxBackground()
    title_text = NeonText(font_size=60, bold=True)
    score_text = NeonText(font_size=32, bold=True)
    
    button_width = 200
    button_height = 50
    button_x = WIDTH // 2 - button_width // 2
    
    retry_button = NeonButton(
        button_x, HEIGHT // 2 + 80,
        button_width, button_height,
        "RETRY",
        base_color=(50, 150, 100),
        glow_color=(100, 255, 150),
        font_size=32
    )
    
    exit_button = NeonButton(
        button_x, HEIGHT // 2 + 150,
        button_width, button_height,
        "EXIT",
        base_color=(150, 50, 80),
        glow_color=(255, 100, 130),
        font_size=32
    )
    
    pygame.mixer.music.load('game_sounds/gameover.mp3')
    pygame.mixer.music.play()
    
    selected_button = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_button = 0
                elif event.key == pygame.K_DOWN:
                    selected_button = 1
                elif event.key == pygame.K_RETURN:
                    if selected_button == 0:
                        music_background()
                        return 'retry'
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if retry_button.is_hovered((x, y)):
                    selected_button = 0
                elif exit_button.is_hovered((x, y)):
                    selected_button = 1
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if retry_button.is_hovered((x, y)):
                    music_background()
                    return 'retry'
                elif exit_button.is_hovered((x, y)):
                    pygame.quit()
                    sys.exit()
        
        parallax_bg.update(0.3)
        parallax_bg.draw(screen)
        
        title_text.draw(
            screen, "GAME OVER",
            (WIDTH // 2, HEIGHT // 2 - 80),
            color=(255, 60, 60),
            glow_color=(255, 100, 100),
            pulse=True
        )
        
        score_text.draw(
            screen, f"Final Score: {score:,}",
            (WIDTH // 2, HEIGHT // 2),
            color=(255, 255, 255),
            glow_color=(200, 200, 255),
            pulse=False
        )
        
        retry_button.draw(screen, selected=selected_button == 0)
        exit_button.draw(screen, selected=selected_button == 1)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return 'exit'


def show_pause_menu(game_screen_snapshot):
    """
    Display semi-transparent pause menu with Resume and Quit buttons.
    Returns: 'resume' to continue playing, 'quit' to exit the game
    """
    clock = pygame.time.Clock()
    parallax_bg = ParallaxBackground()
    title_text = NeonText(font_size=50, bold=True)
    
    button_width = 200
    button_height = 50
    button_x = WIDTH // 2 - button_width // 2
    
    resume_button = NeonButton(
        button_x, HEIGHT // 2 + 20,
        button_width, button_height,
        "RESUME",
        base_color=(50, 120, 180),
        glow_color=(100, 180, 255),
        font_size=32
    )
    
    quit_button = NeonButton(
        button_x, HEIGHT // 2 + 90,
        button_width, button_height,
        "QUIT",
        base_color=(150, 50, 80),
        glow_color=(255, 100, 130),
        font_size=32
    )
    
    selected_button = 0
    
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_button = 0
                elif event.key == pygame.K_DOWN:
                    selected_button = 1
                elif event.key == pygame.K_RETURN:
                    if selected_button == 0:
                        return 'resume'
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    return 'resume'
            
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if resume_button.is_hovered((x, y)):
                    selected_button = 0
                elif quit_button.is_hovered((x, y)):
                    selected_button = 1
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if resume_button.is_hovered((x, y)):
                    return 'resume'
                elif quit_button.is_hovered((x, y)):
                    pygame.quit()
                    sys.exit()
        
        # Update parallax for subtle movement
        parallax_bg.update(0.2)
        
        # Draw game snapshot as base, then overlay
        screen.blit(game_screen_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw parallax with low alpha for depth effect
        parallax_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        parallax_bg.draw(parallax_surface)
        parallax_surface.set_alpha(60)
        screen.blit(parallax_surface, (0, 0))
        
        title_text.draw(
            screen, "PAUSED",
            (WIDTH // 2, HEIGHT // 2 - 80),
            color=(100, 180, 255),
            glow_color=(150, 200, 255),
            pulse=True
        )
        
        resume_button.draw(screen, selected=selected_button == 0)
        quit_button.draw(screen, selected=selected_button == 1)
        
        pygame.display.flip()
        clock.tick(FPS)


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
