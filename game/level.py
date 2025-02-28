# game/level.py
import pygame
import json
import os

class Level:
    def __init__(self, level_file):
        self.physics_tiles = []
        self.decorative_tiles = []
        self.collectibles = []
        self.enemies = []
        self.width = 2000  # Default from your settings
        self.height = 1200
        self.load_level(level_file)

    def load_level(self, level_file):
        if os.path.exists(level_file):
            try:
                with open(level_file, "r") as f:
                    level_data = json.load(f)
                
                for x, y, w, h, index in level_data.get("tiles", []):
                    self.physics_tiles.append((pygame.Rect(x, y, w, h), index))
                for x, y, w, h, index in level_data.get("decor", []):
                    self.decorative_tiles.append((pygame.Rect(x, y, w, h), index))
                for x, y, w, h, index in level_data.get("collectibles", []):
                    self.collectibles.append((pygame.Rect(x, y, w, h), index))
                self.enemies = [(pygame.Rect(x, y, w, h), enemy_type) for x, y, w, h, enemy_type in level_data.get("enemies", [])]
                
                if self.physics_tiles or self.decorative_tiles or self.collectibles or self.enemies:
                    max_x = max(
                        max((t[0].right for t in self.physics_tiles), default=0),
                        max((t[0].right for t in self.decorative_tiles), default=0),
                        max((c[0].right for c in self.collectibles), default=0),
                        max((e[0].right for e in self.enemies), default=0)
                    )
                    max_y = max(
                        max((t[0].bottom for t in self.physics_tiles), default=0),
                        max((t[0].bottom for t in self.decorative_tiles), default=0),
                        max((c[0].bottom for c in self.collectibles), default=0),
                        max((e[0].bottom for e in self.enemies), default=0)
                    )
                    self.width = max(self.width, max_x + 50)
                    self.height = max(self.height, max_y + 50)
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {level_file}: {e}")
                self.create_default_level()
        else:
            self.create_default_level()

    def create_default_level(self):
        for x in range(0, self.width, 50):
            self.physics_tiles.append((pygame.Rect(x, 500, 50, 50), 0))
        self.physics_tiles.append((pygame.Rect(300, 400, 150, 20), 1))
        self.physics_tiles.append((pygame.Rect(500, 300, 150, 20), 2))
        self.collectibles.append((pygame.Rect(350, 350, 32, 32), 0))
        self.collectibles.append((pygame.Rect(550, 250, 32, 32), 1))
        self.enemies.append((pygame.Rect(500, 270, 32, 32), "walker"))
        self.decorative_tiles.append((pygame.Rect(100, 450, 50, 50), 0))