import pygame
from screens.base_screen import draw_screen

class LoginScreen:
    def __init__(self, screen, settings, database):
        self.screen = screen
        self.settings = settings
        self.database = database
        self.bg = pygame.image.load("./Assets/Background/login.png")
        self.username = ""
        self.password = ""
        self.username_active = False
        self.password_active = False
        self.message = ""
        self.success = False

        self.font = pygame.font.Font(None, 32)
        
        self.username_rect = pygame.Rect(262, 192, 438, 45)
        self.password_rect = pygame.Rect(262, 276, 438, 45)
        self.login_button_rect = pygame.Rect(375, 376, 211, 55)
        self.sign_up_button_rect = pygame.Rect(375, 457, 211, 55)

    def handle_input(self, event):
        if event.type == pygame.QUIT:
            return "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.username_rect.collidepoint(event.pos):
                self.username_active = True
                self.password_active = False
            elif self.password_rect.collidepoint(event.pos):
                self.password_active = True
                self.username_active = False
            elif self.login_button_rect.collidepoint(event.pos):
                self.success, self.message = self.database.login_user(self.username, self.password)
                if self.success:
                    logged_username = self.username  
                    self.username = ""
                    self.password = ""
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    return "game", logged_username  
                else:
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(2000)
            
            elif self.sign_up_button_rect.collidepoint(event.pos):
                return "signup"

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.username_active:
                    self.username = self.username[:-1]
                elif self.password_active:
                    self.password = self.password[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.success, self.message = self.database.login_user(self.username, self.password)
                if self.success:
                    logged_username = self.username  
                    self.username = ""
                    self.password = ""
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    return "game", logged_username 
                else:
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(2000)
            else:
                if self.username_active:
                    self.username += event.unicode
                elif self.password_active:
                    self.password += event.unicode

    def draw(self):
        draw_screen(self.screen, self.bg)
        
        username_surface = self.font.render(self.username, True, (255, 255, 255))
        self.screen.blit(username_surface, (self.username_rect.x + 20, self.username_rect.y + 10))
        
        password_surface = self.font.render("*" * len(self.password), True, (255, 255, 255))
        self.screen.blit(password_surface, (self.password_rect.x + 20, self.password_rect.y + 10))
        
        if self.message:
            message_color = (0, 255, 0) if self.success else (255, 0, 0)
            message_surface = self.font.render(self.message, True, message_color)
            message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, self.password_rect.y + 70))
            self.screen.blit(message_surface, message_rect)
            self.message = ""