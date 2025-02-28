import pygame
import os
import random
from config.settings import Settings

settings = Settings()

class Projectile:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.velocity = pygame.Vector2(direction * 5, 0)
        self.animations = [pygame.image.load(os.path.join("Assets", "Enemies", "Lizzard", "Fireball", f"fireball{i}.png")).convert_alpha() for i in range(1, 5)]
        self.frame_index = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.particles = []
        self.remove = False

    def update(self, tiles):
        self.rect.x += self.velocity.x
        
        for tile in tiles:
            if self.rect.colliderect(tile):
                self.spawn_particles()
                self.remove = True
                break
        
        if not self.remove:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.frame_index = (self.frame_index + 1) % len(self.animations)
                self.animation_timer = 0

    def spawn_particles(self):
        for _ in range(10):
            particle = pygame.Rect(self.rect.centerx, self.rect.centery, *settings.particle_size)
            particle_velocity = pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, 0))
            self.particles.append((particle, particle_velocity, settings.particle_lifetime))

    def update_particles(self):
        remaining_particles = []
        for particle, velocity, lifetime in self.particles[:]:
            particle.x += velocity.x
            particle.y += velocity.y
            lifetime -= 1
            if lifetime > 0:
                remaining_particles.append((particle, velocity, lifetime))
        self.particles = remaining_particles
        return self.particles

    def draw(self, screen, camera):
        if not self.remove:
            frame = self.animations[self.frame_index]
            if self.velocity.x < 0:
                frame = pygame.transform.flip(frame, True, False)
            adjusted_rect = camera.apply(self.rect)
            screen.blit(frame, adjusted_rect)
        
        for particle, _, _ in self.particles:
            adjusted_particle_rect = camera.apply(particle)
            pygame.draw.rect(screen, settings.particle_color, adjusted_particle_rect)