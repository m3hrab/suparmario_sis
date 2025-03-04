import pygame

def game_over_screen(screen, settings, score, db, logged_in_user):
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    running = True
    
    print(f"Game over screen, logged_in_user: {logged_in_user}")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "game"
                if event.key == pygame.K_m:
                    return "menu"
        
        screen.fill((0, 0, 0))
        
        # Draw game over text
        title_text = font.render("Game Over!", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 - 60))
        
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 - 20))
        
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 + 20))
        
        menu_text = font.render("Press M to Return to Menu", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 + 60))
        
        screen.blit(title_text, title_rect)
        screen.blit(score_text, score_rect)
        screen.blit(restart_text, restart_rect)
        screen.blit(menu_text, menu_rect)
        
        # Draw leaderboard
        if logged_in_user is None:
            login_text = font.render("Login to view Leaderboard", True, (255, 255, 255))
            login_rect = login_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 + 100))
            screen.blit(login_text, login_rect)
            pygame.display.flip()
        
        else:
            if logged_in_user and logged_in_user.strip():
                top_players = db.get_top_players()
                # print(f"Top players: {top_players}")
                if top_players:
                    leaderboard_title = font.render("Leaderboard - Top 5", True, (255, 255, 0))
                    leaderboard_title_rect = leaderboard_title.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 + 100))
                    screen.blit(leaderboard_title, leaderboard_title_rect)
                    
                    for i, (username, high_score) in enumerate(top_players):
                        player_text = small_font.render(f"{i + 1}. {username}: {high_score}", True, (255, 255, 255))
                        player_rect = player_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 + 130 + i * 30))
                        screen.blit(player_text, player_rect)
                else:
                    no_data_text = font.render("No leaderboard data yet", True, (255, 255, 255))
                    no_data_rect = no_data_text.get_rect(center=(settings.screen_width // 2, settings.screen_height // 2 + 100))
                    screen.blit(no_data_text, no_data_rect)
        
        pygame.display.flip()
        pygame.time.Clock().tick(settings.fps)
    
    return "menu"