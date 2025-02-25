import pygame 
from screens.base_screen import draw_screen

second_menu_screen_bg = pygame.image.load("./Assets/Background/second.png")

def second_menu_screen(screen):
    draw_screen(screen, second_menu_screen_bg)