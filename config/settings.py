import pygame
import os

class Settings:
    def __init__(self):
        # Screen settings
        self.screen_width = 960
        self.screen_height = 540
        self.fps = 60

        # Level settings
        self.level_width = 2000
        self.level_height = 1200
        self.tile_size = 32

        # Object properties
        self.player_size = (32, 32)
        self.enemy_size = (32, 32)
        self.collectible_size = (32, 32)
        self.particle_size = (5, 5)
        self.particle_color = (255, 255, 255)
        self.background_color = (135, 206, 235)
        self.text_color = (0, 0, 0)
        self.game_over_color = (255, 0, 0)

        # Physics settings
        self.gravity = 0.8
        self.player_speed = 5
        self.player_jump_power = -10
        self.enemy_speed = 1

        # Game mechanics
        self.starting_health = 100
        self.damage_amount = 10
        self.attack_cooldown = 60
        self.particle_lifetime = 20
        self.score_per_enemy = 10
        self.score_per_collectible = 5
        self.shoot_cooldown = 90  # For EnemyShooter (1.5s at 60 FPS)

        # Background settings
        self.background_layers = [
            {"file": os.path.join("Assets", "Background", "1.png"), "speed": 0.1},
            {"file": os.path.join("Assets", "Background", "2.png"), "speed": 0.3},
            {"file": os.path.join("Assets", "Background", "3.png"), "speed": 0.5},
            {"file": os.path.join("Assets", "Background", "4.png"), "speed": 0.7},
            {"file": os.path.join("Assets", "Background", "5.png"), "speed": 0.9}
        ]
        self.background_width = 576
        self.background_height = 324  # Scaled to 1080px in game

        # Asset lists
        self.tile_images = [os.path.join("Assets", "tiles", f"{i}.png") for i in range(1, 18)]
        self.decor_images = [os.path.join("Assets", "decor", f"{i}.png") for i in range(1, 31)]
        self.collectible_images = [os.path.join("Assets", "Collectables", f"{i}.png") for i in range(1, 13)]

        # Audio files
        self.audio_files = {
            "coin": os.path.join("Assets", "Audio", "Sound", "coin.wav"),
            "enemy_death": os.path.join("Assets", "Audio", "Sound", "enemy_death.wav"),
            "hurt": os.path.join("Assets", "Audio", "Sound", "hurt.wav"),
            "jump": os.path.join("Assets", "Audio", "Sound", "jump.wav"),
            "shoot": os.path.join("Assets", "Audio", "Sound", "shoot.wav")
        }