import pygame
import os
from game.projectile import Projectile
from config.settings import Settings

settings = Settings()

class Enemy:
    def __init__(self, x, y, tiles, game=None):
        self.rect = pygame.Rect(x, y, *settings.enemy_size)
        self.velocity = pygame.Vector2(-settings.enemy_speed, 0)
        self.gravity = settings.gravity
        self.speed = settings.enemy_speed
        self.game = game
        self.tiles = tiles
        self.snap_to_ground(tiles)
    
    def snap_to_ground(self, tiles):
        temp_rect = self.rect.copy()
        while temp_rect.y < settings.level_height:
            temp_rect.y += 1
            for tile in tiles:
                if temp_rect.colliderect(tile):
                    self.rect.bottom = tile.top
                    return
            if temp_rect.y > self.rect.y + 100:
                break
        self.rect.bottom = 500
    
    def apply_gravity(self):
        self.velocity.y += self.gravity
        self.velocity.y = min(self.velocity.y, 15)
    
    def move_horizontal(self):
        self.rect.x += self.velocity.x
        for tile in self.tiles:
            if self.rect.colliderect(tile):
                if self.velocity.x > 0:
                    self.rect.right = tile.left
                    self.velocity.x = -self.speed
                elif self.velocity.x < 0:
                    self.rect.left = tile.right
                    self.velocity.x = self.speed
    
    def move_vertical(self):
        self.rect.y += self.velocity.y
        on_ground = False
        for tile in self.tiles:
            if self.rect.colliderect(tile):
                if self.velocity.y > 0:
                    self.rect.bottom = tile.top
                    self.velocity.y = 0
                    on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = tile.bottom
                    self.velocity.y = 0
        return on_ground
    
    def update(self, tiles, player):
        pass
    
    def draw(self, screen, camera):
        pass

class EnemyCrab(Enemy):
    def __init__(self, x, y, tiles, game=None):
        super().__init__(x, y, tiles, game)
        self.attack_cooldown = settings.attack_cooldown
        self.attack_timer = 0
        
        self.animations = {
            "idle": [pygame.image.load(os.path.join("Assets", "Enemies", "Crab", "Idle", f"crab-idle{i}.png")).convert_alpha() for i in range(1, 5)],
            "walk": [pygame.image.load(os.path.join("Assets", "Enemies", "Crab", "Walk", f"crab-walk{i}.png")).convert_alpha() for i in range(1, 7)]
        }
        self.current_animation = "walk"
        self.frame_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.facing_right = True
    
    def update(self, tiles, player):
        self.apply_gravity()
        
        self.move_horizontal()
        
        on_ground = self.move_vertical()
        
        if on_ground:
            edge_ahead = pygame.Rect(
                self.rect.x + (self.velocity.x * 10),
                self.rect.bottom, 10, 2
            )
            if not any(edge_ahead.colliderect(tile) for tile in tiles):
                self.velocity.x = -self.velocity.x
                self.facing_right = not self.facing_right
        
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
            self.animation_timer = 0
    
    def attack(self, player):
        if self.attack_timer <= 0 and self.game:
            self.game.take_damage(player)
            self.attack_timer = self.attack_cooldown
    
    def draw(self, screen, camera):
        frame = self.animations[self.current_animation][self.frame_index]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        adjusted_rect = camera.apply(self.rect)
        screen.blit(frame, adjusted_rect)

class EnemyLizard(Enemy):
    def __init__(self, x, y, tiles, game=None):
        super().__init__(x, y, tiles, game)
        self.shoot_cooldown = settings.shoot_cooldown
        self.shoot_timer = 0
        self.projectiles = []
        self.particle_effects = []
        self.shooting = False
        self.shoot_duration = 30
        self.shoot_duration_timer = 0
        
        self.animations = {
            "move": [pygame.image.load(os.path.join("Assets", "Enemies", "Lizzard", "lizard moves", f"lizard-move{i}.png")).convert_alpha() for i in range(1, 4)],
            "shoot": [pygame.image.load(os.path.join("Assets", "Enemies", "Lizzard", "lizard shoots", f"lizard-shoot{i}.png")).convert_alpha() for i in range(1, 5)]
        }
        self.current_animation = "move"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        self.facing_right = False
        self.shoot_range = 400
        self.min_shoot_range = 100
    
    def check_line_of_sight(self, tiles, player):
        direction = 1 if self.facing_right else -1
        start_x = self.rect.centerx
        end_x = player.rect.centerx
        step = direction * 10
        current_x = start_x
        
        vertical_tolerance = 32
        if abs(player.rect.centery - self.rect.centery) > vertical_tolerance:
            return False
        
        if (direction > 0 and player.rect.centerx <= self.rect.centerx) or \
           (direction < 0 and player.rect.centerx >= self.rect.centerx):
            return False
        
        while (direction > 0 and current_x < end_x) or (direction < 0 and current_x > end_x):
            check_point = pygame.Rect(current_x, self.rect.centery - 10, 10, 20)
            for tile in tiles:
                if check_point.colliderect(tile):
                    return False
            current_x += step
        return True

    def update(self, tiles, player):
        self.apply_gravity()
        
        player_dx = player.rect.centerx - self.rect.centerx
        player_dy = player.rect.centery - self.rect.centery
        distance = (player_dx ** 2 + player_dy ** 2) ** 0.5
        
        if self.shooting:
            self.shoot_duration_timer -= 1
            if self.shoot_duration_timer <= 0:
                self.shooting = False
                self.velocity.x = -self.speed if self.velocity.x < 0 else self.speed
                if self.current_animation != "move":
                    self.current_animation = "move"
                    self.frame_index = 0
            else:
                self.velocity.x = 0
                if self.current_animation != "shoot":
                    self.current_animation = "shoot"
                    self.frame_index = 0
                self.facing_right = player_dx > 0
        else:
            self.move_horizontal()
            self.facing_right = self.velocity.x > 0
        
        on_ground = self.move_vertical()
        
        if on_ground and not self.shooting:
            edge_ahead = pygame.Rect(
                self.rect.x + (self.velocity.x * 10),
                self.rect.bottom, 10, 2
            )
            if not any(edge_ahead.colliderect(tile) for tile in tiles):
                self.velocity.x = -self.velocity.x
                self.facing_right = self.velocity.x > 0
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        
        if self.shoot_timer == 0 and not self.shooting:
            if self.min_shoot_range < distance < self.shoot_range and self.check_line_of_sight(tiles, player):
                direction = 1 if self.facing_right else -1
                target_x = player.rect.centerx + (player.velocity.x * 10)
                projectile = Projectile(self.rect.centerx, self.rect.centery, direction)
                self.projectiles.append(projectile)
                self.shoot_timer = self.shoot_cooldown
                self.shooting = True
                self.shoot_duration_timer = self.shoot_duration
        
        for proj in self.projectiles[:]:
            proj.update(tiles)
            if proj.remove:
                self.particle_effects.extend(proj.update_particles())
                self.projectiles.remove(proj)
        
        remaining_particles = []
        for particle, velocity, lifetime in self.particle_effects[:]:
            particle.x += velocity.x
            particle.y += velocity.y
            lifetime -= 1
            if lifetime > 0:
                remaining_particles.append((particle, velocity, lifetime))
        self.particle_effects = remaining_particles
        
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
            self.animation_timer = 0
    
    def draw_projectiles(self, screen, camera):
        for proj in self.projectiles:
            proj.draw(screen, camera)

    def draw(self, screen, camera):
        frame = self.animations[self.current_animation][self.frame_index]
        if self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        adjusted_rect = camera.apply(self.rect)
        screen.blit(frame, adjusted_rect)
        
        for particle, _, _ in self.particle_effects:
            adjusted_particle_rect = camera.apply(particle)
            pygame.draw.rect(screen, settings.particle_color, adjusted_particle_rect)