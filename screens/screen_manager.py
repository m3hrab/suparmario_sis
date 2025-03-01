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
        self.logged_in_user = None
        
        self.screens = {
            "menu": menu_screen,
            "second_menu": second_menu_screen,
            "login": LoginScreen(screen, settings, self.db),
            "signup": SignupScreen(screen, settings, self.db),
            "game": lambda screen: game_screen(screen, self.settings, self.db, self.logged_in_user, level_number=1),
        }
        
        self.buttons = {
            "menu": [(402, 345, 156, 44, "second_menu")],
            "second_menu": [
                (372, 217, 210, 47, "login"),
                (372, 279, 210, 47, "signup"),
                (372, 380, 210, 47, "game"),
                (372, 442, 210, 47, "game")  # Play without login
            ],
            "signup": [
                (375, 376, 211, 55, "game"),
                (375, 457, 211, 55, "login")
            ]
        }
    
    def change_screen(self, new_screen):
        if new_screen:
            if isinstance(new_screen, tuple):  # Handle (screen, username) from login
                screen_name, username = new_screen
                self.logged_in_user = username
                self.current_screen = screen_name
            elif isinstance(new_screen, str) and ":" in new_screen:
                screen_name, level = new_screen.split(":")
                if screen_name == "game":
                    self.screens["game"] = lambda screen: game_screen(screen, self.settings, self.db, self.logged_in_user, level_number=int(level))
                    self.current_screen = "game"
            elif new_screen in self.screens:
                self.current_screen = new_screen
            print(f"Changed screen to {self.current_screen}, logged_in_user: {self.logged_in_user}")
    
    def handle_input(self, event):
        if self.current_screen in ["login", "signup"]:
            result = self.screens[self.current_screen].handle_input(event)
            if result:
                if isinstance(result, tuple) and result[0] == "game":
                    self.logged_in_user = result[1]  # Set from tuple
                    print(f"Logged in as {self.logged_in_user} from {self.current_screen}")
                    self.change_screen("game")
                elif isinstance(result, str):
                    if result == "game" and self.current_screen == "signup":
                        self.logged_in_user = self.screens["signup"].username
                        print(f"Logged in as {self.logged_in_user} from signup")
                    self.change_screen(result)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, (x, y, w, h, next_screen) in enumerate(self.buttons.get(self.current_screen, [])):
                    if x < event.pos[0] < x + w and y < event.pos[1] < y + h:
                        print(f"Button clicked: {next_screen}")
                        if self.current_screen == "second_menu" and idx == 3:
                            self.logged_in_user = None
                            print("Playing without login")
                        self.change_screen(next_screen)
                        break
    
    def update(self):
        if self.current_screen in ["login", "signup"]:
            self.screens[self.current_screen].draw()
        else:
            result = self.screens[self.current_screen](self.screen)
            if result:
                self.change_screen(result)