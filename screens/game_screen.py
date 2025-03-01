# screens/game_screen.py
import pygame
import os
import random
from game.camera import Camera
from game.enemy import EnemyWalker, EnemyShooter
from game.level import Level
from game.player import Player
from game.projectile import Projectile
from game.particle import Particle
from config.settings import Settings
from screens.game_over import game_over_screen

def game_screen(screen, settings, db, logged_in_user, level_number=1):
    pygame.mixer.init()
    clock = pygame.time.Clock()
    
    # Load level
    level_file = os.path.join("levels", f"level{level_number}.json")
    if not os.path.exists(level_file):
        print(f"Level {level_number} not found, defaulting to level1.json")
        level_file = os.path.join("levels", "level1.json")
    level = Level(level_file)
    
    # Load sprites and audio
    backgrounds = [pygame.image.load(os.path.join(bg["file"])).convert() for bg in settings.background_layers]
    for i in range(len(backgrounds)):
        backgrounds[i] = pygame.transform.scale(backgrounds[i], (settings.screen_width, 1080))
    tile_sprites = [pygame.image.load(file).convert_alpha() for file in settings.tile_images]
    decor_sprites = [pygame.image.load(file).convert_alpha() for file in settings.decor_images]
    collectible_sprites = [pygame.image.load(file).convert_alpha() for file in settings.collectible_images]
    heart_full = pygame.image.load(settings.heart_full_image).convert_alpha()
    heart_empty = pygame.image.load(settings.heart_empty_image).convert_alpha()
    sounds = {key: pygame.mixer.Sound(file) for key, file in settings.audio_files.items()}
    
    # Scale hearts
    heart_size = (32, 32)
    heart_full = pygame.transform.scale(heart_full, heart_size)
    heart_empty = pygame.transform.scale(heart_empty, heart_size)
    
    # Initialize game objects
    game_instance = Game(settings)
    player = Player(settings.screen_width // 2, 400, game_instance)
    enemies = []
    for enemy_rect, enemy_type in level.enemies:
        if enemy_type == "walker":
            enemies.append(EnemyWalker(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
        elif enemy_type == "shooter":
            enemies.append(EnemyShooter(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
    camera = Camera(level.width, level.height, settings.screen_width, settings.screen_height)
    camera.update(player.rect)
    
    score = 0
    running = True
    font = pygame.font.Font(None, 36)
    
    collectible_frame = 0
    collectible_animation_speed = 0.2
    collectible_timer = 0
    
    # Screen shake variables
    shake_offset = pygame.Vector2(0, 0)
    
    # Screen flash variables
    flash_surface = pygame.Surface((settings.screen_width, settings.screen_height), pygame.SRCALPHA)
    
    print(f"Game started, logged_in_user: {logged_in_user}")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
        
        if game_instance.player_lives > 0:
            # Game running
            player.update([t[0] for t in level.physics_tiles])
            if player.velocity.y < 0:
                sounds["jump"].play()
            
            for enemy in enemies[:]:
                enemy.update([t[0] for t in level.physics_tiles], player)
                if isinstance(enemy, EnemyShooter) and enemy.shoot_timer == settings.shoot_cooldown - 1:
                    sounds["shoot"].play()
                if player.rect.colliderect(enemy.rect):
                    if player.dashing:
                        sounds["enemy_death"].play()
                        player.spawn_particles(enemy.rect.centerx, enemy.rect.centery)
                        enemies.remove(enemy)
                        score += settings.score_per_enemy
                    elif isinstance(enemy, EnemyWalker):
                        game_instance.take_damage(player)
                        sounds["hurt"].play()
                        player.rect.x = settings.screen_width // 2
                        player.rect.y = 400
            
            for collectible in level.collectibles[:]:
                if player.rect.colliderect(collectible[0]):
                    sounds["coin"].play()
                    level.collectibles.remove(collectible)
                    score += settings.score_per_collectible
            
            for enemy in enemies:
                if isinstance(enemy, EnemyShooter):
                    for proj in enemy.projectiles[:]:
                        if proj.rect.colliderect(player.rect):
                            game_instance.take_damage(player)
                            sounds["hurt"].play()
                            player.rect.x = settings.screen_width // 2
                            player.rect.y = 400
                            enemy.projectiles.remove(proj)
            
            camera.update(player.rect)
            
            collectible_timer += collectible_animation_speed
            if collectible_timer >= 1:
                collectible_frame = (collectible_frame + 1) % len(collectible_sprites)
                collectible_timer = 0
        
        # Screen shake update
        if game_instance.shake_duration > 0:
            shake_offset = pygame.Vector2(
                random.uniform(-game_instance.shake_intensity, game_instance.shake_intensity),
                random.uniform(-game_instance.shake_intensity, game_instance.shake_intensity)
            )
            game_instance.shake_duration -= 1
            print(f"Shake active: duration={game_instance.shake_duration}, offset={shake_offset}")
        else:
            shake_offset = pygame.Vector2(0, 0)
        
        # Screen flash update
        if game_instance.flash_alpha > 0:
            game_instance.flash_alpha -= game_instance.flash_max_alpha / game_instance.flash_duration
            game_instance.flash_alpha = max(0, game_instance.flash_alpha)
            flash_surface.fill((255, 0, 0, int(game_instance.flash_alpha)))
            print(f"Flash active: alpha={game_instance.flash_alpha}")
        
        # Draw
        screen.fill(settings.background_color)
        
        for i, bg in enumerate(backgrounds):
            parallax_offset = camera.apply_parallax(i)
            bg_width = bg.get_width()
            bg_height = bg.get_height()
            start_x = -(parallax_offset.x % bg_width) + shake_offset.x
            y_offset = -(parallax_offset.y % bg_height) - (bg_height - settings.screen_height) // 2 + shake_offset.y
            num_tiles_x = int(settings.screen_width / bg_width) + 2
            num_tiles_y = int(settings.screen_height / bg_height) + 2
            for j in range(num_tiles_x):
                for k in range(num_tiles_y):
                    x_pos = start_x + (j * bg_width)
                    y_pos = y_offset + (k * bg_height)
                    screen.blit(bg, (x_pos, y_pos))
        
        for dec, index in level.decorative_tiles:
            sprite = decor_sprites[index]
            adjusted_rect = camera.apply(dec).move(shake_offset.x, shake_offset.y)
            screen.blit(sprite, adjusted_rect)
        
        for tile, index in level.physics_tiles:
            sprite = tile_sprites[index]
            adjusted_rect = camera.apply(tile).move(shake_offset.x, shake_offset.y)
            screen.blit(sprite, adjusted_rect)
        
        for coll, index in level.collectibles:
            sprite = collectible_sprites[collectible_frame]
            adjusted_rect = camera.apply(coll).move(shake_offset.x, shake_offset.y)
            screen.blit(sprite, adjusted_rect)
        
        player.draw(screen, camera)
        
        for particle in player.particles:
            adjusted_particle_rect = camera.apply(particle.rect).move(shake_offset.x, shake_offset.y)
            pygame.draw.rect(screen, settings.particle_color, adjusted_particle_rect)
        
        for enemy in enemies:
            enemy.draw(screen, camera)
            if isinstance(enemy, EnemyShooter):
                enemy.draw_projectiles(screen, camera)
        
        # Draw screen flash overlay
        if game_instance.flash_alpha > 0:
            screen.blit(flash_surface, (0, 0))
        
        # HUD
        level_text = font.render(f"Level {level_number}", True, settings.text_color)
        screen.blit(level_text, (10, 10))
        
        score_text = font.render(f"Score: {score}", True, settings.text_color)
        score_rect = score_text.get_rect(center=(settings.screen_width // 2, 20))
        screen.blit(score_text, score_rect)
        
        for i in range(3):
            if i < game_instance.player_lives:
                screen.blit(heart_full, (settings.screen_width - 40 - i * 40, 10))
            else:
                screen.blit(heart_empty, (settings.screen_width - 40 - i * 40, 10))
        
        # Check win/lose conditions
        next_level = level_number + 1
        next_level_file = os.path.join("levels", f"level{next_level}.json")
        
        if game_instance.player_lives <= 0:
            running = False
            if logged_in_user and logged_in_user.strip():  # Check for non-empty username
                db.update_score(logged_in_user, score)
                print(f"Score updated for {logged_in_user}: {score}")
            result = game_over_screen(screen, settings, score, db, logged_in_user)
            if result == "game":
                return f"game:{level_number}"
            elif result == "menu" or result is None:
                return "menu"
        elif not level.collectibles and os.path.exists(next_level_file):
            running = False
            if logged_in_user and logged_in_user.strip():
                db.update_score(logged_in_user, score)
                print(f"Score updated for {logged_in_user}: {score}")
            return f"game:{next_level}"
        
        pygame.display.flip()
        clock.tick(settings.fps)
    
    if logged_in_user and logged_in_user.strip():
        db.update_score(logged_in_user, score)
        print(f"Score updated for {logged_in_user}: {score} on quit")
    return "menu"

class Game:
    def __init__(self, settings):
        self.player_lives = settings.starting_lives
        # Effect variables
        self.shake_duration = 0
        self.shake_intensity = 5
        self.flash_alpha = 0
        self.flash_max_alpha = 150
        self.flash_duration = 10
        
    def take_damage(self, player):
        self.player_lives -= 1
        print(f"Player lost a life! Lives remaining: {self.player_lives}")
        # Trigger effects on damage
        self.shake_duration = 10
        self.flash_alpha = self.flash_max_alpha
        player.spawn_particles(player.rect.centerx, player.rect.centery, count=10)
        print("Effects triggered: shake, flash, particles")