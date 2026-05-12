```markdown
# Knot-Today

A modern Hangman game built with Python and Pygame. Features a sleek "Void Amber" theme, smooth animations, fullscreen support, and a robust scoring system.

![Knot-Today](screenshot.png)

## Features

- **Modern UI** - Glassmorphism design with deep void backgrounds and amber accents
- **Multiple Categories** - Technology, Nature, History, and Science (50+ words each)
- **Scoring System** - Earn points for correct guesses, build streaks for multipliers
- **Hint System** - Spend 50 points to reveal a letter
- **Fullscreen Support** - Press F11 to toggle fullscreen mode
- **Pause Menu** - Resume, mute/unmute, or exit to main menu
- **Smooth Animations** - Hangman draws sequentially with easing functions
- **High Score Tracking** - Saves your best score locally
- **Responsive Layout** - UI scales properly when window is resized

## Requirements

- Python 3.8 or higher
- Pygame 2.0 or higher

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/Knot-Today.git
cd Knot-Today
```

### Step 2: Install Dependencies
```bash
pip install pygame
```

### Step 3: Run the Game
```bash
python main.py
```

### Optional: Create a Desktop Shortcut (Windows)
Create a file called `run.bat` in the game folder with:
```bat
@echo off
title Knot-Today
cd /d "%~dp0"
python main.py
pause
```
Double-click `run.bat` to launch the game.

## How to Play

| Action | Control |
|--------|---------|
| Select Category | Click a category button |
| Guess a Letter | Click on-screen keyboard or type letter |
| Use Hint | Click HINT button (costs 50 points) |
| Pause Game | Click MENU button |
| Toggle Fullscreen | Press `F11` |
| Return to Menu | Press `ESC` |
| Quit Game | Close window or `Ctrl+C` in terminal |

## Scoring

| Action | Points |
|--------|--------|
| Correct letter (short word < 5 letters) | +10 |
| Correct letter (long word ≥ 5 letters) | +25 |
| Streak bonus | +5 per consecutive correct guess |
| Winning the round | +100 |
| Using a hint | -50 |

## Project Structure

```
Knot-Today/
├── assets/
│   └── sounds/          # Sound effects (optional)
├── data/
│   ├── words.json       # Word categories and lists
│   └── highscore.json   # Persistent high score storage
├── game_logic.py        # Game rules and state management
├── game_state.py        # State machine (menu/gameplay/game over)
├── main.py              # Entry point and main loop
├── renderer.py          # UI rendering and animations
├── settings.py          # Configuration constants
├── sound_manager.py     # Audio handling
├── theme.py             # Color palette
├── utils.py             # Helper functions
└── README.md
```

## Customization

### Changing Colors
Edit `theme.py` to modify the color scheme. All colors are defined as RGB/RGBA tuples.

### Adding Words
Edit `data/words.json` to add new categories or words. Follow the existing format:
```json
{
    "category_name": ["WORD1", "WORD2", "WORD3"]
}
```

### Adjusting Difficulty
Edit `settings.py` to change:
- `MAX_LIVES` - Number of wrong guesses allowed (default: 6)
- `HINT_COST` - Points required for a hint (default: 50)
- `FPS` - Game speed (default: 60)

## Troubleshooting

### "No module named 'pygame'"
```bash
pip install pygame
```

### Game runs slowly
- Ensure your Python version is 3.8+
- Try reducing `FPS` in `settings.py` to 30
- Close other applications to free up resources

### Sound not working
- Sound is optional - the game runs without it
- Place `.wav` files in `assets/sounds/` (click.wav, correct.wav, wrong.wav, win.wav, lose.wav)

### Fullscreen shows black borders
- Press `F11` twice to reset the display
- The game automatically scales to your monitor's resolution

## Credits

Developed as a collaborative project demonstrating:
- MVC architecture in Pygame
- Git branching and team workflow
- Modern UI/UX design principles
- Game state management
- Performance optimization techniques

## License

This project is for educational purposes. Feel free to use and modify.

---
*Knot-Today - Where every letter counts*
```
