# screens/game_screen.py
import pygame
import os
import random
from game.camera import Camera
from game.enemy import EnemyCrab, EnemyLizard
from game.level import Level
from game.player import Player
from game.projectile import Projectile
from game.particle import Particle
from config.settings import Settings
from screens.game_over import game_over_screen

def game_screen(screen, settings, db, logged_in_user, level_number=1):
    pygame.mixer.init()
    clock = pygame.time.Clock()
    
    def reset_level():
        """Reset level state, including player lives."""
        nonlocal level, player, enemies, score, collectible_frame, collectible_timer, game_instance
        level_file = os.path.join("levels", f"level{level_number}.json")
        if not os.path.exists(level_file):
            level_file = os.path.join("levels", "level1.json")
        level = Level(level_file)
        
        game_instance = Game(settings)  # Reset lives and related state
        player = Player(settings.screen_width // 2, 400, game_instance)
        
        enemies.clear()
        for enemy_rect, enemy_type in level.enemies:
            if enemy_type == "walker":
                enemies.append(EnemyCrab(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
            elif enemy_type == "shooter":
                enemies.append(EnemyLizard(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
        
        score = 0
        collectible_frame = 0
        collectible_timer = 0
        camera.update(player.rect)
        print(f"Level {level_number} restarted, lives reset to {game_instance.player_lives}")

    def load_next_level():
        """Load next level, maintaining score and lives."""
        nonlocal level, player, enemies, collectible_frame, collectible_timer, level_number
        level_file = os.path.join("levels", f"level{level_number}.json")
        if not os.path.exists(level_file):
            level_file = os.path.join("levels", "level1.json")
        level = Level(level_file)
        
        player = Player(settings.screen_width // 2, 400, game_instance)  # Keep game_instance for lives
        
        enemies.clear()
        for enemy_rect, enemy_type in level.enemies:
            if enemy_type == "walker":
                enemies.append(EnemyCrab(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
            elif enemy_type == "shooter":
                enemies.append(EnemyLizard(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
        
        collectible_frame = 0
        collectible_timer = 0
        camera.update(player.rect)
        print(f"Transitioned to Level {level_number}, score: {score}, lives: {game_instance.player_lives}")

    # Load level (initial)
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
    shield_image = pygame.image.load(os.path.join("Assets", "Shield", "Shield.png")).convert_alpha()
    shield_image = pygame.transform.scale(shield_image, (32, 32))
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
            enemies.append(EnemyCrab(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
        elif enemy_type == "shooter":
            enemies.append(EnemyLizard(enemy_rect.x, enemy_rect.y, [t[0] for t in level.physics_tiles], game_instance))
    camera = Camera(level.width, level.height, settings.screen_width, settings.screen_height)
    camera.update(player.rect)
    
    score = 0
    running = True
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    collectible_frame = 0
    collectible_animation_speed = 0.2
    collectible_timer = 0
    
    # Screen shake variables
    shake_offset = pygame.Vector2(0, 0)
    
    # Screen flash variables
    flash_surface = pygame.Surface((settings.screen_width, settings.screen_height), pygame.SRCALPHA)
    
    # Transition variables
    transition_alpha = 0
    transition_timer = 0
    transitioning = False
    next_level_number = None
    endgame_message = False
    message_timer = 0
    
    # Play background music and ambience
    pygame.mixer.music.load(settings.audio_files["music"])
    pygame.mixer.music.play(-1)
    sounds["ambience"].play(-1)
    
    print(f"Game started, logged_in_user: {logged_in_user}")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    reset_level()
                elif event.key == pygame.K_f and game_instance.shield_cooldown <= 0:
                    game_instance.shield_timer = 180
                    game_instance.shield_active = True
                    game_instance.shield_cooldown = 480
                    print("Shield activated")
        
        # Check lose condition first
        if game_instance.player_lives <= 0:
            running = False
            if logged_in_user and logged_in_user.strip():
                user_id = db.get_user_id(logged_in_user)
                if user_id:
                    db.log_game_session(user_id, score, game_instance.lives_lost)
                    db.update_score(logged_in_user, score)
                    print(f"Score updated for {logged_in_user}: {score}")
            result = game_over_screen(screen, settings, score, db, logged_in_user)
            if result == "game":
                return f"game:{1}"  # Restart at level 1
            elif result == "menu" or result is None:
                return "menu"
        
        # Game logic if player still has lives
        if not transitioning and not endgame_message:
            player.update([t[0] for t in level.physics_tiles])
            if player.velocity.y < 0:
                sounds["jump"].play()
            if player.dashing and player.dash_timer == player.dash_duration - 1:
                sounds["dash"].play()
            
            if game_instance.damage_cooldown > 0:
                game_instance.damage_cooldown -= 1
            if game_instance.shield_timer > 0:
                game_instance.shield_timer -= 1
                if game_instance.shield_timer <= 0:
                    game_instance.shield_active = False
                    print("Shield deactivated")
            if game_instance.shield_cooldown > 0:
                game_instance.shield_cooldown -= 1
            
            for enemy in enemies[:]:
                enemy.update([t[0] for t in level.physics_tiles], player)
                if isinstance(enemy, EnemyLizard) and enemy.shoot_timer == settings.shoot_cooldown - 1:
                    sounds["shoot"].play()
                if player.rect.colliderect(enemy.rect):
                    if player.velocity.y > 0 and enemy.rect.top < player.rect.bottom <= enemy.rect.top + enemy.rect.height and game_instance.damage_cooldown <= 0:
                        sounds["enemy_death"].play()
                        player.spawn_particles(enemy.rect.centerx, enemy.rect.centery)
                        enemies.remove(enemy)
                        score += settings.score_per_enemy
                        print(f"Enemy ({type(enemy).__name__}) defeated by jump at ({enemy.rect.x}, {enemy.rect.y}), player bottom: {player.rect.bottom}, enemy top: {enemy.rect.top}, score: {score}")
                        player.velocity.y = -5
                    elif player.dashing and game_instance.damage_cooldown <= 0:
                        sounds["enemy_death"].play()
                        player.spawn_particles(enemy.rect.centerx, enemy.rect.centery)
                        enemies.remove(enemy)
                        score += settings.score_per_enemy
                        print(f"Enemy ({type(enemy).__name__}) defeated by dash at ({enemy.rect.x}, {enemy.rect.y}), dashing: {player.dashing}, score: {score}")
                    elif game_instance.damage_cooldown <= 0:
                        game_instance.take_damage(player)
                        sounds["hurt"].play()
                        player.rect.x = settings.screen_width // 2
                        player.rect.y = 400
                        print(f"Player respawned at ({player.rect.x}, {player.rect.y}) due to enemy ({type(enemy).__name__}) contact")
            
            for collectible in level.collectibles[:]:
                if player.rect.colliderect(collectible[0]):
                    sounds["coin"].play()
                    level.collectibles.remove(collectible)
                    score += settings.score_per_collectible
            
            for enemy in enemies:
                if isinstance(enemy, EnemyLizard):
                    for proj in enemy.projectiles[:]:
                        if proj.rect.colliderect(player.rect) and game_instance.damage_cooldown <= 0:
                            if game_instance.shield_active:
                                proj.spawn_particles()
                                enemy.projectiles.remove(proj)
                                print(f"Shield blocked fireball at ({proj.rect.x}, {proj.rect.y})")
                            else:
                                game_instance.take_damage(player)
                                sounds["hurt"].play()
                                player.rect.x = settings.screen_width // 2
                                player.rect.y = 400
                                enemy.projectiles.remove(proj)
                                print(f"Player respawned at ({player.rect.x}, {player.rect.y}) due to projectile hit")
            
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
        
        # Transition update
        if transitioning:
            transition_timer += 1
            if transition_timer <= 60:
                transition_alpha = (transition_timer / 60) * 255
            else:
                transition_alpha = 255 - ((transition_timer - 60) / 60) * 255
            if transition_timer >= 120:
                transitioning = False
                transition_timer = 0
                transition_alpha = 0
                if next_level_number:
                    level_number = next_level_number
                    load_next_level()
                    next_level_number = None
                else:
                    endgame_message = True
                    message_timer = 180
        
        # Endgame message update
        if endgame_message:
            message_timer -= 1
            if message_timer <= 0:
                running = False
                if logged_in_user and logged_in_user.strip():
                    user_id = db.get_user_id(logged_in_user)
                    if user_id:
                        db.log_game_session(user_id, score, game_instance.lives_lost)
                        db.update_score(logged_in_user, score)
                        print(f"Score updated for {logged_in_user}: {score}")
                result = game_over_screen(screen, settings, score, db, logged_in_user)
                if result == "game":
                    return f"game:{1}"
                elif result == "menu" or result is None:
                    return "menu"
        
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
        
        if game_instance.shield_active:
            shield_rect = camera.apply(player.rect)
            screen.blit(shield_image, shield_rect)
        
        for particle in player.particles:
            adjusted_particle_rect = camera.apply(particle.rect).move(shake_offset.x, shake_offset.y)
            pygame.draw.rect(screen, settings.particle_color, adjusted_particle_rect)
        
        for enemy in enemies:
            enemy.draw(screen, camera)
            if isinstance(enemy, EnemyLizard):
                enemy.draw_projectiles(screen, camera)
        
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
        
        dash_status = "Dash: Ready" if player.dash_cooldown_timer <= 0 else f"Dash: {player.dash_cooldown_timer // 60}s"
        dash_text = small_font.render(dash_status, True, settings.text_color)
        dash_rect = dash_text.get_rect(center=(settings.screen_width // 2 - 50, 50))
        screen.blit(dash_text, dash_rect)
        
        shield_status = "Shield: Ready" if game_instance.shield_cooldown <= 0 else f"Shield: {game_instance.shield_cooldown // 60}s"
        shield_text = small_font.render(shield_status, True, settings.text_color)
        shield_rect = shield_text.get_rect(center=(settings.screen_width // 2 + 50, 50))
        screen.blit(shield_text, shield_rect)
        
        # Draw transition overlay
        if transitioning:
            transition_surface = pygame.Surface((settings.screen_width, settings.screen_height), pygame.SRCALPHA)
            transition_surface.fill((0, 0, 0, int(transition_alpha)))
            screen.blit(transition_surface, (0, 0))
        
        # Draw endgame message
        if endgame_message:
            message_text = font.render("All levels completed", True, settings.text_color)
            message_rect = message_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2))
            screen.blit(message_text, message_rect)
        
        # Check level completion
        if not level.collectibles and not transitioning and not endgame_message:
            next_level_file = os.path.join("levels", f"level{level_number + 1}.json")
            if os.path.exists(next_level_file):
                transitioning = True
                next_level_number = level_number + 1
            else:
                transitioning = True
                next_level_number = None
        
        pygame.display.flip()
        clock.tick(settings.fps)
    
    pygame.mixer.music.stop()
    sounds["ambience"].stop()
    
    if logged_in_user and logged_in_user.strip():
        user_id = db.get_user_id(logged_in_user)
        if user_id:
            db.log_game_session(user_id, score, game_instance.lives_lost)
            db.update_score(logged_in_user, score)
            print(f"Score updated for {logged_in_user}: {score} on quit")
    return "menu"

class Game:
    def __init__(self, settings):
        self.player_lives = settings.starting_lives
        self.Damage_AMOUNT = settings.damage_amount
        self.shake_duration = 0
        self.shake_intensity = 5
        self.flash_alpha = 0
        self.flash_max_alpha = 150
        self.flash_duration = 10
        self.lives_lost = 0
        self.damage_cooldown = 0
        self.shield_active = False
        self.shield_timer = 0
        self.shield_cooldown = 0
        
    def take_damage(self, player):
        if self.damage_cooldown <= 0:
            self.player_lives -= 1
            self.lives_lost += 1
            self.damage_cooldown = 30
            print(f"Player lost a life! Lives remaining: {self.player_lives}")
            self.shake_duration = 10
            self.flash_alpha = self.flash_max_alpha
            player.spawn_particles(player.rect.centerx, player.rect.centery, count=10)
            print("Effects triggered: shake, flash, particles")
            player.rect.x = 480
            player.rect.y = 400