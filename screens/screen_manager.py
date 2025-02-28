# screens/screen_manager.py
import pygame
from screens.menu_screen import menu_screen
from screens.second_menu_screen import second_menu_screen
from screens.login_screen import LoginScreen
from screens.signup_screen import SignupScreen
from screens.game_screen import game_screen

class ScreenManager:
    def __init__(self, screen, settings, db):
        self.screen = screen
        self.settings = settings
        self.current_screen = "menu"
        self.db = db
        
        self.screens = {
            "menu": menu_screen,
            "second_menu": second_menu_screen,
            "login": LoginScreen(screen, settings, self.db),
            "signup": SignupScreen(screen, settings, self.db),
            "game": lambda screen: game_screen(screen, self.settings, self.db, level_number=1)
        }
        
        self.buttons = {
            "menu": [(402, 345, 156, 44, "second_menu")],
            "second_menu": [
                (372, 217, 210, 47, "login"),
                (372, 279, 210, 47, "signup"),
                (372, 380, 210, 47, "game")
            ],
            "signup": [
                (375, 376, 211, 55, "game"),
                (375, 457, 211, 55, "login")
            ]
        }
    
    def change_screen(self, new_screen):
        if new_screen:
            if isinstance(new_screen, str) and ":" in new_screen:
                screen_name, level = new_screen.split(":")
                if screen_name == "game":
                    self.screens["game"] = lambda screen: game_screen(screen, self.settings, self.db, level_number=int(level))
                    self.current_screen = "game"
            elif new_screen in self.screens:
                self.current_screen = new_screen
    
    def handle_input(self, event):
        if self.current_screen in ["login", "signup"]:
            result = self.screens[self.current_screen].handle_input(event)
            if isinstance(result, str):
                self.change_screen(result)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for x, y, w, h, next_screen in self.buttons.get(self.current_screen, []):
                    if x < event.pos[0] < x + w and y < event.pos[1] < y + h:
                        print(f"Button clicked: {next_screen}")
                        self.change_screen(next_screen)
                        break
    
    def update(self):
        if self.current_screen in ["login", "signup"]:
            self.screens[self.current_screen].draw()
        else:
            result = self.screens[self.current_screen](self.screen)
            if result:
                self.change_screen(result)