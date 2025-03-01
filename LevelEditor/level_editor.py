# LevelEditor/level_editor.py
import pygame
import json
import os
from settings import *

pygame.init()

class Camera:
    def __init__(self, level_width, level_height, screen_width, screen_height):
        self.offset = pygame.Vector2(0, 0)
        self.level_width = level_width
        self.level_height = level_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def update(self, mouse_pos, keys):
        if mouse_pos[0] > self.screen_width - 50 and self.offset.x < self.level_width - self.screen_width:
            self.offset.x += 5
        elif mouse_pos[0] < 50 and self.offset.x > 0:
            self.offset.x -= 5
        if keys[pygame.K_LEFT] and self.offset.x > 0:
            self.offset.x -= 5
        elif keys[pygame.K_RIGHT] and self.offset.x < self.level_width - self.screen_width:
            self.offset.x += 5
        if mouse_pos[1] > self.screen_height - 50 and self.offset.y < self.level_height - self.screen_height:
            self.offset.y += 5
        elif mouse_pos[1] < 50 and self.offset.y > 0:
            self.offset.y -= 5
        if keys[pygame.K_UP] and self.offset.y > 0:
            self.offset.y -= 5
        elif keys[pygame.K_DOWN] and self.offset.y < self.level_height - self.screen_height:
            self.offset.y += 5
        self.offset.x = max(0, min(self.offset.x, self.level_width - self.screen_width))
        self.offset.y = max(0, min(self.offset.y, self.level_height - self.screen_height))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def apply_parallax(self, layer_index):
        layer_speed = BACKGROUND_LAYERS[layer_index]["speed"]
        parallax_offset = pygame.Vector2(self.offset.x * layer_speed, self.offset.y * layer_speed)
        return parallax_offset

class LevelEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Level Editor")
        self.clock = pygame.time.Clock()
        self.tiles = []
        self.collectibles = []
        self.enemies = []
        self.decor = []
        self.tile_size = TILE_SIZE
        self.level_width = LEVEL_WIDTH
        self.level_height = LEVEL_HEIGHT
        self.running = True
        self.camera = Camera(self.level_width, self.level_height, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.font = pygame.font.Font(None, 36)
        
        # Load assets
        self.tile_sprites = [pygame.image.load(file).convert_alpha() for file in TILE_IMAGES]
        self.decor_sprites = [pygame.image.load(file).convert_alpha() for file in DECOR_IMAGES]
        self.collectible_sprites = [pygame.image.load(file).convert_alpha() for file in COLLECTIBLE_IMAGES]
        self.backgrounds = [pygame.image.load(os.path.join(bg["file"])).convert() for bg in BACKGROUND_LAYERS]
        for i in range(len(self.backgrounds)):
            self.backgrounds[i] = pygame.transform.scale(self.backgrounds[i], (SCREEN_WIDTH, 1080))
        self.enemy_colors = {"walker": ENEMY_COLOR, "shooter": (255, 0, 255)}
        
        # Selection system
        self.item_types = ["tile", "decor", "collectible", "walker", "shooter"]
        self.selected_type = "tile"
        self.selected_index = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        self.camera.update(mouse_pos, keys)
        
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.add_object(mouse_pos)
        if mouse_buttons[2]:
            self.remove_object(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.save_level()
                if event.key == pygame.K_l:
                    self.load_level()
                if event.key == pygame.K_t:
                    self.selected_type = "tile"
                    self.selected_index = 0
                if event.key == pygame.K_d:
                    self.selected_type = "decor"
                    self.selected_index = 0
                if event.key == pygame.K_c:
                    self.selected_type = "collectible"
                    self.selected_index = 0
                if event.key == pygame.K_w:
                    self.selected_type = "walker"
                    self.selected_index = 0
                if event.key == pygame.K_f:
                    self.selected_type = "shooter"
                    self.selected_index = 0
                if event.key == pygame.K_q:
                    self.running = False
            # Selection switching with mouse wheel (moved outside KEYDOWN)
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up
                    self.selected_index = (self.selected_index - 1) % self.get_max_index()
                elif event.y < 0:  # Scroll down
                    self.selected_index = (self.selected_index + 1) % self.get_max_index()

    def get_max_index(self):
        if self.selected_type == "tile":
            return len(self.tile_sprites)
        elif self.selected_type == "decor":
            return len(self.decor_sprites)
        elif self.selected_type == "collectible":
            return len(self.collectible_sprites)
        else:  # walker, shooter
            return 1

    def add_object(self, pos):
        grid_x = ((pos[0] + self.camera.offset.x) // self.tile_size) * self.tile_size
        grid_y = ((pos[1] + self.camera.offset.y) // self.tile_size) * self.tile_size
        
        if self.selected_type == "tile":
            new_rect = pygame.Rect(grid_x, grid_y, self.tile_size, self.tile_size)
            if not any(tile[0].colliderect(new_rect) for tile in self.tiles):
                self.tiles.append((new_rect, self.selected_index))
        elif self.selected_type == "decor":
            new_rect = pygame.Rect(grid_x, grid_y, self.tile_size, self.tile_size)
            if not any(dec[0].colliderect(new_rect) for dec in self.decor):
                self.decor.append((new_rect, self.selected_index))
        elif self.selected_type == "collectible":
            new_rect = pygame.Rect(grid_x, grid_y, *COLLECTIBLE_SIZE)
            if not any(coll[0].colliderect(new_rect) for coll in self.collectibles):
                self.collectibles.append((new_rect, self.selected_index))
        elif self.selected_type in ["walker", "shooter"]:
            new_rect = pygame.Rect(grid_x, grid_y, *ENEMY_SIZE)
            if not any(enemy[0].colliderect(new_rect) for enemy in self.enemies):
                self.enemies.append((new_rect, self.selected_type))

    def remove_object(self, pos):
        check_x = pos[0] + self.camera.offset.x
        check_y = pos[1] + self.camera.offset.y
        
        for tile in self.tiles[:]:
            if tile[0].collidepoint(check_x, check_y):
                self.tiles.remove(tile)
        for dec in self.decor[:]:
            if dec[0].collidepoint(check_x, check_y):
                self.decor.remove(dec)
        for coll in self.collectibles[:]:
            if coll[0].collidepoint(check_x, check_y):
                self.collectibles.remove(coll)
        for enemy in self.enemies[:]:
            if enemy[0].collidepoint(check_x, check_y):
                self.enemies.remove(enemy)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw parallax backgrounds
        for i, bg in enumerate(self.backgrounds):
            parallax_offset = self.camera.apply_parallax(i)
            bg_width = bg.get_width()
            bg_height = bg.get_height()
            start_x = -(parallax_offset.x % bg_width)
            y_offset = -(parallax_offset.y % bg_height) - (bg_height - SCREEN_HEIGHT) // 2
            num_tiles_x = int(SCREEN_WIDTH / bg_width) + 2
            num_tiles_y = int(SCREEN_HEIGHT / bg_height) + 2
            for j in range(num_tiles_x):
                for k in range(num_tiles_y):
                    x_pos = start_x + (j * bg_width)
                    y_pos = y_offset + (k * bg_height)
                    self.screen.blit(bg, (x_pos, y_pos))
        
        # Draw grid
        start_x = -(self.camera.offset.x % self.tile_size)
        start_y = -(self.camera.offset.y % self.tile_size)
        for x in range(int(start_x), SCREEN_WIDTH, self.tile_size):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(int(start_y), SCREEN_HEIGHT, self.tile_size):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
            
        # Draw decor (no physics)
        for dec, index in self.decor:
            sprite = self.decor_sprites[index]
            adjusted_rect = dec.move(-self.camera.offset.x, -self.camera.offset.y)
            self.screen.blit(sprite, adjusted_rect)
            
        # Draw tiles (physics)
        for tile, index in self.tiles:
            sprite = self.tile_sprites[index]
            adjusted_rect = tile.move(-self.camera.offset.x, -self.camera.offset.y)
            self.screen.blit(sprite, adjusted_rect)
            
        # Draw collectibles (static in editor)
        for coll, index in self.collectibles:
            sprite = self.collectible_sprites[index]
            adjusted_rect = coll.move(-self.camera.offset.x, -self.camera.offset.y)
            self.screen.blit(sprite, adjusted_rect)
            
        # Draw enemies
        for enemy, enemy_type in self.enemies:
            pygame.draw.rect(self.screen, self.enemy_colors[enemy_type],
                            (enemy.x - self.camera.offset.x, enemy.y - self.camera.offset.y,
                             enemy.width, enemy.height))
            
        # Draw instructions and selection info
        mouse_pos = pygame.mouse.get_pos()
        grid_col = (mouse_pos[0] + self.camera.offset.x) // self.tile_size
        grid_row = (mouse_pos[1] + self.camera.offset.y) // self.tile_size
        
        instructions = [
            "T: Tiles | D: Decor | C: Collectibles | W: Walker | F: Shooter",
            "S: Save | L: Load | Q: Quit",
            "Hold Left Click: Place | Hold Right Click: Remove",
            "Mouse Wheel: Switch Item | Arrows/Mouse Edges: Scroll",
            f"Grid Position: Row {grid_row}, Col {grid_col}",
            f"Selected: {self.selected_type.capitalize()} {self.selected_index + 1}/{self.get_max_index()}"
        ]
        for i, text in enumerate(instructions):
            render = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(render, (10, 10 + i * 30))
        
        # Draw preview at cursor
        preview_rect = pygame.Rect(mouse_pos[0], mouse_pos[1], self.tile_size, self.tile_size)
        if self.selected_type == "tile":
            preview = self.tile_sprites[self.selected_index]
            self.screen.blit(preview, preview_rect)
        elif self.selected_type == "decor":
            preview = self.decor_sprites[self.selected_index]
            self.screen.blit(preview, preview_rect)
        elif self.selected_type == "collectible":
            preview = self.collectible_sprites[self.selected_index]
            self.screen.blit(preview, preview_rect.move(0, 8))
        elif self.selected_type in ["walker", "shooter"]:
            pygame.draw.rect(self.screen, self.enemy_colors[self.selected_type], preview_rect)

        pygame.display.flip()

    def save_level(self):
        level_data = {
            "tiles": [(t[0].x, t[0].y, t[0].width, t[0].height, t[1]) for t in self.tiles],
            "decor": [(d[0].x, d[0].y, d[0].width, d[0].height, d[1]) for d in self.decor],
            "collectibles": [(c[0].x, c[0].y, c[0].width, c[0].height, c[1]) for c in self.collectibles],
            "enemies": [(e[0].x, e[0].y, e[0].width, e[0].height, e[1]) for e in self.enemies]
        }
        with open("level.json", "w") as f:
            json.dump(level_data, f)
        print("Level saved to level.json!")

    def load_level(self):
        if os.path.exists("level.json"):
            try:
                with open("level.json", "r") as f:
                    level_data = json.load(f)
                
                self.tiles.clear()
                self.decor.clear()
                self.collectibles.clear()
                self.enemies.clear()
                
                for x, y, w, h, index in level_data.get("tiles", []):
                    self.tiles.append((pygame.Rect(x, y, w, h), index))
                for x, y, w, h, index in level_data.get("decor", []):
                    self.decor.append((pygame.Rect(x, y, w, h), index))
                for x, y, w, h, index in level_data.get("collectibles", []):
                    self.collectibles.append((pygame.Rect(x, y, w, h), index))
                for x, y, w, h, enemy_type in level_data.get("enemies", []):
                    self.enemies.append((pygame.Rect(x, y, w, h), enemy_type))
                
                print("Level loaded from level.json!")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading level.json: {e}")
        else:
            print("No level.json file found to load.")

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
    pygame.quit()