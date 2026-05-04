# game_logic.py
import random
from utils import calculate_points

class HangmanGame:
    def __init__(self, secret_word, category=None, max_lives=6):
        self.secret_word = secret_word.upper()
        self.category = category
        self.max_lives = max_lives
        self.hint_cost = 50
        self.reset()

    def reset(self):
        self.lives = self.max_lives
        self.guessed_letters = set()
        self.game_over = False
        self.won = False
        self.score = 0
        self.streak = 0
        self.last_guess_correct = None
        self.last_guess_letter = None
        self.newly_revealed_positions = []

    def guess(self, letter, is_hint_guess=False):
        if self.game_over:
            return False, "Game finished", 0, []
        
        letter = letter.upper()
        if letter in self.guessed_letters:
            return False, "Already guessed", 0, []
        
        self.guessed_letters.add(letter)
        self.last_guess_letter = letter
        
        if letter not in self.secret_word:
            self.lives -= 1
            self.streak = 0
            self.last_guess_correct = False
            self.newly_revealed_positions = []
            if self.lives <= 0:
                self.game_over = True
                self.won = False
            return False, "Wrong!", 0, []
        
        self.last_guess_correct = True
        self.newly_revealed_positions = [i for i, ch in enumerate(self.secret_word) if ch == letter]
        count = len(self.newly_revealed_positions)
        
        # ONLY add points if this is NOT a hint guess
        if not is_hint_guess:
            self.streak += 1
            points = calculate_points(self.secret_word, True, self.streak) * count
            self.score += points
        else:
            points = 0
        
        if all(ch in self.guessed_letters for ch in self.secret_word):
            self.game_over = True
            self.won = True
        
        return True, f"+{points}" if points > 0 else "Revealed!", points, self.newly_revealed_positions

    def can_afford_hint(self):
        return self.score >= self.hint_cost and not self.game_over

    def use_hint(self):
        if not self.can_afford_hint():
            return None, "Not enough points!"
        
        hidden = [ch for ch in self.secret_word if ch not in self.guessed_letters]
        if hidden:
            self.score -= self.hint_cost
            return random.choice(hidden), f"-{self.hint_cost} points"
        return None, "No letters left!"

    def get_display_word(self):
        return " ".join([ch if ch in self.guessed_letters else "_" for ch in self.secret_word])

    def get_status(self):
        return {
            "lives": self.lives,
            "max_lives": self.max_lives,
            "guessed": sorted(self.guessed_letters),
            "display": self.get_display_word(),
            "game_over": self.game_over,
            "won": self.won,
            "secret": self.secret_word if self.game_over else None,
            "score": self.score,
            "streak": self.streak,
            "hint_cost": self.hint_cost,
            "can_afford_hint": self.can_afford_hint(),
            "category": self.category
        }