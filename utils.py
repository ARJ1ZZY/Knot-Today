import json
import random
from pathlib import Path

def load_word_bank(filepath="data/words.json"):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Word bank missing: {filepath}")
    with open(path, 'r') as f:
        return json.load(f)

def get_random_word(category=None):
    bank = load_word_bank()
    if category and category in bank:
        return random.choice(bank[category]).upper()
    all_words = []
    for words in bank.values():
        all_words.extend(words)
    return random.choice(all_words).upper()

def validate_guess(guess, guessed_set):
    if not guess.isalpha():
        return False, "Only letters allowed."
    if len(guess) != 1:
        return False, "Enter one letter."
    if guess in guessed_set:
        return False, "Already guessed."
    return True, None

def clear_screen():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')