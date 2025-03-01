# LevelEditor/settings.py
import os

# Screen settings
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

# Level settings
LEVEL_WIDTH = 2000
LEVEL_HEIGHT = 1200
TILE_SIZE = 32


# Object properties
PLAYER_SIZE = (32, 64)
ENEMY_SIZE = (32, 32)
COLLECTIBLE_SIZE = (20, 20)
COLLECTIBLE_COLOR = (255, 255, 0)
PARTICLE_SIZE = (5, 5)
PARTICLE_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (135, 206, 235)
GRID_COLOR = (200, 200, 200)
TEXT_COLOR = (0, 0, 0)
GAME_OVER_COLOR = (255, 0, 0)
ENEMY_COLOR = (0, 0, 255)

# Physics settings
GRAVITY = 0.8
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = -15
ENEMY_SPEED = 2

# Game mechanics
STARTING_HEALTH = 100
DAMAGE_AMOUNT = 10
ATTACK_COOLDOWN = 60
PARTICLE_LIFETIME = 20
SCORE_PER_ENEMY = 10
SCORE_PER_COLLECTIBLE = 5

# Background settings
BACKGROUND_LAYERS = [
    {"file": os.path.join("Assets", "Background", "1.png"), "speed": 0.1},
    {"file": os.path.join("Assets", "Background", "2.png"), "speed": 0.3},
    {"file": os.path.join("Assets", "Background", "3.png"), "speed": 0.5},
    {"file": os.path.join("Assets", "Background", "4.png"), "speed": 0.7},
    {"file": os.path.join("Assets", "Background", "5.png"), "speed": 0.9}
]
BACKGROUND_WIDTH = 576
BACKGROUND_HEIGHT = 324

# Asset lists
TILE_IMAGES = [os.path.join("Assets", "tiles", f"{i}.png") for i in range(1, 20)]
DECOR_IMAGES = [os.path.join("Assets", "decor", f"{i}.png") for i in range(1, 31)]
COLLECTIBLE_IMAGES = [os.path.join("Assets", "Collectables", f"{i}.png") for i in range(1, 13)]