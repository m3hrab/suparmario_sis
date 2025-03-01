import pygame
from LevelEditor.settings import *

class Camera:
    def __init__(self, level_width, level_height, screen_width, screen_height):
        self.offset = pygame.Vector2(0, 0)
        self.level_width = level_width
        self.level_height = level_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def update(self, mouse_pos, keys):
        if mouse_pos[0] > self.screen_width - 50 and self.offset.x < self.level_width - self.screen_width:
            self.offset.x += 5
        elif mouse_pos[0] < 50 and self.offset.x > 0:
            self.offset.x -= 5
        if keys[pygame.K_LEFT] and self.offset.x > 0:
            self.offset.x -= 5
        elif keys[pygame.K_RIGHT] and self.offset.x < self.level_width - self.screen_width:
            self.offset.x += 5
        if mouse_pos[1] > self.screen_height - 50 and self.offset.y < self.level_height - self.screen_height:
            self.offset.y += 5
        elif mouse_pos[1] < 50 and self.offset.y > 0:
            self.offset.y -= 5
        if keys[pygame.K_UP] and self.offset.y > 0:
            self.offset.y -= 5
        elif keys[pygame.K_DOWN] and self.offset.y < self.level_height - self.screen_height:
            self.offset.y += 5
        self.offset.x = max(0, min(self.offset.x, self.level_width - self.screen_width))
        self.offset.y = max(0, min(self.offset.y, self.level_height - self.screen_height))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def apply_parallax(self, layer_index):
        layer_speed = BACKGROUND_LAYERS[layer_index]["speed"]
        parallax_offset = pygame.Vector2(self.offset.x * layer_speed, self.offset.y * layer_speed)
        return parallax_offset