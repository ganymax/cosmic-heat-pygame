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
    """Display game over screen with interactive retry/exit buttons."""
    clock = pygame.time.Clock()
    parallax_bg = ParallaxBackground()
    title_text = NeonText(font_size=60, bold=True)
    score_text = NeonText(font_size=32, bold=True)
    
    pygame.mixer.music.load('game_sounds/gameover.mp3')
    pygame.mixer.music.play()
    
    button_width = 200
    button_height = 50
    button_x = WIDTH // 2 - button_width // 2
    
    retry_button = NeonButton(
        button_x, HEIGHT // 2 + 100,
        button_width, button_height,
        "RETRY",
        base_color=(50, 150, 100),
        glow_color=(100, 255, 150)
    )
    
    exit_button = NeonButton(
        button_x, HEIGHT // 2 + 170,
        button_width, button_height,
        "EXIT",
        base_color=(150, 50, 80),
        glow_color=(255, 100, 130)
    )
    
    selected_button = 0
    
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
                        music_background()
                        return "retry"
                    else:
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
                    return "retry"
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


def show_pause_screen(game_surface):
    """Display pause screen with semi-transparent overlay and resume/quit buttons."""
    clock = pygame.time.Clock()
    title_text = NeonText(font_size=50, bold=True)
    
    button_width = 200
    button_height = 50
    button_x = WIDTH // 2 - button_width // 2
    
    resume_button = NeonButton(
        button_x, HEIGHT // 2 + 30,
        button_width, button_height,
        "RESUME",
        base_color=(50, 150, 100),
        glow_color=(100, 255, 150)
    )
    
    quit_button = NeonButton(
        button_x, HEIGHT // 2 + 100,
        button_width, button_height,
        "QUIT",
        base_color=(150, 50, 80),
        glow_color=(255, 100, 130)
    )
    
    selected_button = 0
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 30, 180))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    return "resume"
                elif event.key == pygame.K_UP:
                    selected_button = 0
                elif event.key == pygame.K_DOWN:
                    selected_button = 1
                elif event.key == pygame.K_RETURN:
                    if selected_button == 0:
                        return "resume"
                    else:
                        pygame.quit()
                        sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if resume_button.is_hovered((x, y)):
                    selected_button = 0
                elif quit_button.is_hovered((x, y)):
                    selected_button = 1
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if resume_button.is_hovered((x, y)):
                    return "resume"
                elif quit_button.is_hovered((x, y)):
                    pygame.quit()
                    sys.exit()
        
        screen.blit(game_surface, (0, 0))
        screen.blit(overlay, (0, 0))
        
        title_text.draw(
            screen, "PAUSED",
            (WIDTH // 2, HEIGHT // 2 - 60),
            color=(200, 200, 255),
            glow_color=(150, 150, 255),
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
