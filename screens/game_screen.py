from screens.base_screen import draw_screen
import pygame
bg = pygame.image.load("./Assets/Background/game.png")
bg = pygame.transform.scale(bg, (960, 540))
def game_screen(screen):
    draw_screen(screen, bg)
