import pygame
from screens.screen_manager import ScreenManager
from auth.auth import Database
from config.settings import Settings

def main():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
    pygame.display.set_caption("2D Space Platformer")
    db = Database()
    screen_manager = ScreenManager(screen, settings, db)
    
    
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            screen_manager.handle_input(event)
        
        screen_manager.update()
        pygame.display.flip()
        pygame.time.Clock().tick(settings.fps)
    
    pygame.quit()
    db.close()

if __name__ == "__main__":
    main()


