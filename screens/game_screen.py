# screens/game_screen.py
import pygame
import os
from game.camera import Camera
from game.enemy import EnemyWalker, EnemyShooter
from game.level import Level
from game.player import Player
from game.projectile import Projectile
from game.particle import Particle
from config.settings import Settings
from screens.game_over import game_over_screen

def game_screen(screen, settings, db, level_number=1):
    pygame.mixer.init()
    clock = pygame.time.Clock()
    
    # Load level
    level_file = os.path.join("levels", f"level{level_number}.json")
    if not os.path.exists(level_file):
        print(f"Level {level_number} not found, defaulting to level1.json")
        level_file = os.path.join("levels", "level1.json")
    level = Level(level_file)
    
    # Load sprites
    backgrounds = [pygame.image.load(os.path.join(bg["file"])).convert() for bg in settings.background_layers]
    for i in range(len(backgrounds)):
        backgrounds[i] = pygame.transform.scale(backgrounds[i], (settings.screen_width, 1080))
    tile_sprites = [pygame.image.load(file).convert_alpha() for file in settings.tile_images]
    decor_sprites = [pygame.image.load(file).convert_alpha() for file in settings.decor_images]
    collectible_sprites = [pygame.image.load(file).convert_alpha() for file in settings.collectible_images]
    
    # Load audio
    sounds = {key: pygame.mixer.Sound(file) for key, file in settings.audio_files.items()}
    
    # Initialize game objects
    game_instance = Game()
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
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
        
        if game_instance.player_health > 0 and level.collectibles:
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
                        player.spawn_kill_particles(enemy.rect.centerx, enemy.rect.centery)
                        enemies.remove(enemy)
                        score += settings.score_per_enemy
                    elif isinstance(enemy, EnemyWalker):
                        enemy.attack(player)
                        sounds["hurt"].play()
            
            for collectible in level.collectibles[:]:
                if player.rect.colliderect(collectible[0]):
                    sounds["coin"].play()
                    level.collectibles.remove(collectible)
                    score += settings.score_per_collectible
            
            camera.update(player.rect)
            
            collectible_timer += collectible_animation_speed
            if collectible_timer >= 1:
                collectible_frame = (collectible_frame + 1) % len(collectible_sprites)
                collectible_timer = 0
        
        # Draw
        screen.fill(settings.background_color)
        
        for i, bg in enumerate(backgrounds):
            parallax_offset = camera.apply_parallax(i)
            bg_width = bg.get_width()
            bg_height = bg.get_height()
            start_x = -(parallax_offset.x % bg_width)
            y_offset = -(parallax_offset.y % bg_height) - (bg_height - settings.screen_height) // 2
            num_tiles_x = int(settings.screen_width / bg_width) + 2
            num_tiles_y = int(settings.screen_height / bg_height) + 2
            for j in range(num_tiles_x):
                for k in range(num_tiles_y):
                    x_pos = start_x + (j * bg_width)
                    y_pos = y_offset + (k * bg_height)
                    screen.blit(bg, (x_pos, y_pos))
        
        for dec, index in level.decorative_tiles:
            sprite = decor_sprites[index]
            adjusted_rect = camera.apply(dec)
            screen.blit(sprite, adjusted_rect)
        
        for tile, index in level.physics_tiles:
            sprite = tile_sprites[index]
            adjusted_rect = camera.apply(tile)
            screen.blit(sprite, adjusted_rect)
        
        for coll, index in level.collectibles:
            sprite = collectible_sprites[collectible_frame]
            adjusted_rect = camera.apply(coll)
            screen.blit(sprite, adjusted_rect)
        
        player.draw(screen, camera)
        
        for particle in player.particles:
            adjusted_particle_rect = camera.apply(particle.rect)
            pygame.draw.rect(screen, settings.particle_color, adjusted_particle_rect)
        
        for enemy in enemies:
            enemy.draw(screen, camera)
            if isinstance(enemy, EnemyShooter):
                enemy.draw_projectiles(screen, camera)
        
        score_text = font.render(f"Score: {score}", True, settings.text_color)
        health_text = font.render(f"Health: {game_instance.player_health}", True, settings.text_color)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))
        
        # Check win/lose conditions
        next_level = level_number + 1
        next_level_file = os.path.join("levels", f"level{next_level}.json")
        
        if game_instance.player_health <= 0 or not level.collectibles:
            running = False
            if not level.collectibles and os.path.exists(next_level_file):
                # Aadvance to next level
                return f"game:{next_level}"
            else:
                # Game over 
                result = game_over_screen(screen, settings, score)
                if result == "game":
                    return f"game:{level_number}"  # Restart current level
                elif result == "menu" or result is None:
                    return "menu"
        
        pygame.display.flip()
        clock.tick(settings.fps)
    
    return "menu"

class Game:
    def __init__(self):
        self.player_health = Settings().starting_health
        
    def take_damage(self, amount):
        self.player_health -= amount
        # print(f"{amount} damage,health: {self.player_health}")