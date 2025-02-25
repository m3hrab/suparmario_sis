import pygame 
from screens.base_screen import draw_screen

menu_screen_bg = pygame.image.load("./Assets/Background/main.png")

# play_btn_rect = pygame.Rect(402, 345, 156, 44)
def menu_screen(screen):
    draw_screen(screen, menu_screen_bg)
