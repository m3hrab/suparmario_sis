import pygame
import random
from config.settings import Settings

settings = Settings()

class Particle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, *settings.particle_size)
        self.velocity = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, -1))
        self.lifetime = settings.particle_lifetime

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0