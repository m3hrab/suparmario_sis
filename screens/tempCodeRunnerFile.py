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