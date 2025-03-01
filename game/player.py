import pygame
from game.particle import Particle
from config.settings import Settings
import random 


settings = Settings()
class Player:
    def __init__(self, x, y, game=None):
        self.rect = pygame.Rect(x, y, *settings.player_size)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = settings.player_speed
        self.jump_power = settings.player_jump_power
        self.gravity = settings.gravity
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 15
        self.dash_speed = 15
        self.dash_cooldown = 60
        self.dash_cooldown_timer = 0
        self.facing_right = True
        self.game = game
        self.particles = []
        
        self.animations = {
            "idle": [pygame.image.load(file).convert_alpha() for file in [
                "Assets/Player/Player-Idle/idle-01.png",
                "Assets/Player/Player-Idle/idle-02.png"
            ]],
            "run": [pygame.image.load(file).convert_alpha() for file in [
                "Assets/Player/Player-Run/Run-01.png",
                "Assets/Player/Player-Run/Run-02.png",
                "Assets/Player/Player-Run/Run-03.png",
                "Assets/Player/Player-Run/Run-04.png",
                "Assets/Player/Player-Run/Run-05.png",
                "Assets/Player/Player-Run/Run-06.png",
                "Assets/Player/Player-Run/Run-07.png",
                "Assets/Player/Player-Run/Run-08.png"
            ]]
        }
        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0

    def update(self, tiles):
        keys = pygame.key.get_pressed()
        
        self.velocity.x = 0
        if not self.dashing:
            if keys[pygame.K_LEFT]:
                self.velocity.x = -self.speed
                self.facing_right = False
                if self.current_animation != "run":
                    self.current_animation = "run"
                    self.frame_index = 0
            elif keys[pygame.K_RIGHT]:
                self.velocity.x = self.speed
                self.facing_right = True
                if self.current_animation != "run":
                    self.current_animation = "run"
                    self.frame_index = 0
            else:
                if self.current_animation != "idle":
                    self.current_animation = "idle"
                    self.frame_index = 0
        
        if keys[pygame.K_SPACE] and not self.dashing and self.dash_cooldown_timer == 0:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            if self.current_animation != "run":
                self.current_animation = "run"
                self.frame_index = 0
        
        if self.dashing:
            self.velocity.x = self.dash_speed if self.facing_right else -self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
        elif self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        if keys[pygame.K_UP] and self.on_ground(tiles):
            self.velocity.y = self.jump_power
        
        self.velocity.y += self.gravity
        self.velocity.y = min(self.velocity.y, 15)
        
        self.move(tiles)
        
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
            self.animation_timer = 0
        
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

    def move(self, tiles):
        self.rect.x += self.velocity.x
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity.x > 0:
                    self.rect.right = tile.left
                elif self.velocity.x < 0:
                    self.rect.left = tile.right
        
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.level_width, settings.level_height))
        
        self.rect.y += self.velocity.y
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity.y > 0:
                    self.rect.bottom = tile.top
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = tile.bottom
                    self.velocity.y = 0

    def on_ground(self, tiles):
        self.rect.y += 2
        on_ground = any(self.rect.colliderect(tile) for tile in tiles)
        self.rect.y -= 2
        return on_ground

    def spawn_particles(self, x, y, count=15):
        """Spawn particles at given position with specified count."""
        for _ in range(count):
            particle = Particle(x, y)
            particle.velocity.x = random.uniform(-3, 3)
            particle.velocity.y = random.uniform(-3, 0)
            self.particles.append(particle)

    def draw(self, screen, camera):
        frame = self.animations[self.current_animation][self.frame_index]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        adjusted_rect = camera.apply(self.rect)
        screen.blit(frame, adjusted_rect)