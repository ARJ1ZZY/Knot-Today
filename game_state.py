# game_state.py
from enum import Enum

class GameState(Enum):
    MAIN_MENU = "main_menu"
    GAMEPLAY = "gameplay"
    GAME_OVER = "game_over"
    PAUSED = "paused"

class StateManager:
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
    
    def change_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state
    
    def get_state(self):
        return self.current_state