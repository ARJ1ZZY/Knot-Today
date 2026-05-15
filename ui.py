# ui.py
from utils import clear_screen

class TerminalRenderer:
    HANGMAN_STATES = [
        """
  +---+
      |
      |
      |
      |
=========
        """,
        """
  +---+
  |   |
      |
      |
      |
=========
        """,
        """
  +---+
  |   |
  O   |
      |
      |
=========
        """,
        """
  +---+
  |   |
  O   |
  |   |
      |
=========
        """,
        """
  +---+
  |   |
  O   |
 /|   |
      |
=========
        """,
        """
  +---+
  |   |
  O   |
 /|\\  |
      |
=========
        """,
        """
  +---+
  |   |
  O   |
 /|\\  |
 /    |
=========
        """,
        """
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
=========
        """
    ]

    @classmethod
    def draw(cls, game_state):
        clear_screen()
        status = game_state
        max_lives = status["max_lives"]
        lives = status["lives"]

        hangman_idx = min(max_lives - lives, len(cls.HANGMAN_STATES) - 1)
        print(cls.HANGMAN_STATES[hangman_idx])

        print(f"\nLives: {lives}/{max_lives}")
        print(f"\nWord: {status['display']}")
        print(f"\nGuessed: {' '.join(status['guessed']) if status['guessed'] else 'None'}")

        if status["game_over"]:
            if status["won"]:
                print("\n=== YOU WIN! ===")
            else:
                print(f"\n=== GAME OVER ===\nWord was: {status['secret']}")