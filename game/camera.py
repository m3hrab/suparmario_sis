import pygame
from config.settings import Settings

settings = Settings()

class Camera:
    def __init__(self, level_width, level_height, screen_width, screen_height):
        self.offset = pygame.Vector2(0, 0)
        self.level_width = level_width
        self.level_height = level_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.follow_speed = 0.1
        
    def update(self, target):
        target_x = target.centerx - self.screen_width // 2
        target_y = target.centery - self.screen_height // 2
        self.offset.x += (target_x - self.offset.x) * self.follow_speed
        self.offset.y += (target_y - self.offset.y) * self.follow_speed
        self.offset.x = max(0, min(self.offset.x, self.level_width - self.screen_width))
        self.offset.y = max(0, min(self.offset.y, self.level_height - self.screen_height))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def apply_parallax(self, layer_index):
        """Apply parallax scrolling for background layers."""
        layer_speed = settings.background_layers[layer_index]["speed"]
        parallax_offset = pygame.Vector2(self.offset.x * layer_speed, self.offset.y * layer_speed)
        return parallax_offset