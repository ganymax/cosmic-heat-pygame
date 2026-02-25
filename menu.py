import sys
import random

import pygame
import pygame.mixer

from classes.constants import WIDTH, HEIGHT, BLACK
from cosmic_ui import ParallaxBackground, NeonButton


def animate_screen(screen, parallax_bg):
    """Screen shake animation with parallax background."""
    for i in range(20):
        parallax_bg.update(2.0)
        parallax_bg.draw(screen)
        pygame.display.flip()
        pygame.time.wait(10)
        
        parallax_bg.update(2.0)
        parallax_bg.draw(screen)
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        shake_surface = screen.copy()
        screen.fill(BLACK)
        screen.blit(shake_surface, (offset_x, offset_y))
        pygame.display.flip()
        pygame.time.wait(10)


pygame.mixer.init()
pygame.init()
pygame.mixer.music.load('game_sounds/menu.mp3')
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)
pygame.mixer.set_num_channels(20)
for i in range(20):
    channel = pygame.mixer.Channel(i)
    channel.set_volume(0.25)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Main Menu")
clock = pygame.time.Clock()

# Parallax background
parallax_bg = ParallaxBackground()

logo_img = pygame.image.load('images/ch.png').convert_alpha()
logo_x = (WIDTH - logo_img.get_width()) // 2
logo_y = 50

# Neon buttons
button_width = 220
button_height = 55
button_x = WIDTH // 2 - button_width // 2

play_button = NeonButton(
    button_x, HEIGHT // 2 - 30,
    button_width, button_height,
    "PLAY",
    base_color=(50, 150, 100),
    glow_color=(100, 255, 150)
)

exit_button = NeonButton(
    button_x, HEIGHT // 2 + 50,
    button_width, button_height,
    "EXIT",
    base_color=(150, 50, 80),
    glow_color=(255, 100, 130)
)

explosion_sound = pygame.mixer.Sound('game_sounds/explosions/explosion1.wav')
explosion_sound.set_volume(0.25)
selected_button = 0
show_menu = True

joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()


while show_menu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if play_button.is_hovered((x, y)):
                explosion_sound.play()
                animate_screen(screen, parallax_bg)
                show_menu = False
                import main
                main.main()
                break
            elif exit_button.is_hovered((x, y)):
                pygame.quit()
                sys.exit()

        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            if play_button.is_hovered((x, y)):
                selected_button = 0
            elif exit_button.is_hovered((x, y)):
                selected_button = 1

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_button = 0
            elif event.key == pygame.K_DOWN:
                selected_button = 1
            elif event.key == pygame.K_RETURN:
                if selected_button == 0:
                    explosion_sound.play()
                    animate_screen(screen, parallax_bg)
                    show_menu = False
                    import main
                    main.main()
                    break
                elif selected_button == 1:
                    pygame.quit()
                    sys.exit()

        if joystick:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if selected_button == 0:
                        explosion_sound.play()
                        animate_screen(screen, parallax_bg)
                        show_menu = False
                        import main
                        main.main()
                        break
                    elif selected_button == 1:
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:
                    selected_button = 0
                elif event.value[1] == -1:
                    selected_button = 1

    # Update and draw parallax background
    parallax_bg.update(0.5)
    parallax_bg.draw(screen)

    # Draw logo
    screen.blit(logo_img, (logo_x, logo_y))

    # Draw neon buttons
    play_button.draw(screen, selected=selected_button == 0)
    exit_button.draw(screen, selected=selected_button == 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
