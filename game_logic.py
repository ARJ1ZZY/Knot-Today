class HangmanGame:
    def __init__(self, secret_word, max_lives=6):
        self.secret_word = secret_word.upper()
        self.max_lives = max_lives
        self.reset()

    def reset(self):
        self.lives = self.max_lives
        self.guessed_letters = set()
        self.game_over = False
        self.won = False

    def guess(self, letter):
        if self.game_over:
            return False, "Game already finished."

        letter = letter.upper()
        if letter in self.guessed_letters:
            return False, "Letter already used."

        self.guessed_letters.add(letter)

        if letter not in self.secret_word:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.won = False
            return False, "Wrong guess."

        if all(ch in self.guessed_letters for ch in self.secret_word):
            self.game_over = True
            self.won = True

        return True, "Correct!"

    def get_display_word(self):
        return " ".join([ch if ch in self.guessed_letters else "_" for ch in self.secret_word])

    def hint(self):
        if self.game_over:
            return False, "Game already finished."
        
        available_letters = [ch for ch in self.secret_word if ch not in self.guessed_letters]
        if not available_letters:
            return False, "No hints available."
        
        hint_letter = available_letters[0]  # Simple hint: first available letter
        success, msg = self.guess(hint_letter)
        return success, f"Hint: {hint_letter} - {msg}"

    def get_status(self):
        return {
            "lives": self.lives,
            "max_lives": self.max_lives,
            "guessed": sorted(self.guessed_letters),
            "display": self.get_display_word(),
            "game_over": self.game_over,
            "won": self.won,
            "secret": self.secret_word if self.game_over else None
        }