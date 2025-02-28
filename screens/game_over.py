import pygame

def game_over_screen(screen, settings, score):
    font = pygame.font.Font(None, 36)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Exit game entirely
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "game"  # Restart (will need level number handling)
                if event.key == pygame.K_m:
                    return "menu"  # Back to menu
        
        screen.fill((0, 0, 0))  # Black background
        title_text = font.render("Game Over!", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        menu_text = font.render("Press M to Return to Menu", True, (255, 255, 255))
        
        screen.blit(title_text, (settings.screen_width // 2 - 80, settings.screen_height // 2 - 60))
        screen.blit(score_text, (settings.screen_width // 2 - 100, settings.screen_height // 2 - 20))
        screen.blit(restart_text, (settings.screen_width // 2 - 100, settings.screen_height // 2 + 20))
        screen.blit(menu_text, (settings.screen_width // 2 - 120, settings.screen_height // 2 + 60))
        
        pygame.display.flip()
        pygame.time.Clock().tick(settings.fps)
    
    return "menu"