import sys
import random

import pygame
import pygame.mixer

from classes.constants import WIDTH, HEIGHT, BLACK
from cosmic_ui import ParallaxBackground, NeonButton


def animate_screen(screen, parallax_bg):
    for i in range(0, 20):
        parallax_bg.update(2.0)
        parallax_bg.draw(screen)
        pygame.display.flip()
        pygame.time.wait(10)
        parallax_bg.update(2.0)
        parallax_bg.draw(screen)
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

parallax_bg = ParallaxBackground()

logo_img = pygame.image.load('images/ch.png').convert_alpha()
logo_x = (WIDTH - logo_img.get_width()) // 2
logo_y = 50

play_button = NeonButton(
    WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50,
    "Play",
    base_color=(50, 200, 100),
    glow_color=(100, 255, 150)
)
quit_button = NeonButton(
    WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50,
    "Exit",
    base_color=(200, 80, 80),
    glow_color=(255, 120, 120)
)

pygame.mixer.music.load('game_sounds/menu.mp3')
pygame.mixer.music.play(-1)
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
            if play_button.collidepoint((x, y)):
                explosion_sound.play()
                animate_screen(screen, parallax_bg)
                show_menu = False
                import main
                main.main()
                break
            elif quit_button.collidepoint((x, y)):
                pygame.quit()
                sys.exit()

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
                    screen.fill(BLACK)
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
                        screen.fill(BLACK)
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

    parallax_bg.update(0.5)
    parallax_bg.draw(screen)

    screen.blit(logo_img, (logo_x, logo_y))

    play_button.draw(screen, selected=selected_button == 0)
    quit_button.draw(screen, selected=selected_button == 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
