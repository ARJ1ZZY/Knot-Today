# Knot-Today-K

A modern, Pygame-based implementation of the classic Hangman word-guessing game with enhanced visuals, sound effects, and category-based gameplay.

## Description

**Knot-Today-K** brings the timeless word-guessing challenge into the modern era with a polished graphical interface. Choose from various word categories, enjoy visual feedback systems, and experience progressive difficulty indicators as you attempt to guess the secret word before running out of lives.

## Features

### Game Mechanics
- **Word Categories**: Select from themed word banks including animals, countries, and more
- **Lives System**: Start with 6 lives, with visual warnings as they decrease
- **Multiple Input Methods**: Use mouse clicks on virtual keyboard or physical keyboard input
- **Random Word Selection**: Choose a specific category or let the game pick randomly

### Visual Design
- **Dynamic Hangman Graphics**: ASCII-style drawing with color-coded progression
- **Responsive Layout**: Centered hangman figure, positioned answer display, and organized keyboard
- **Color-Coded Lives**:
  - 4+ lives: White (normal)
  - 3 lives: Yellow (caution)
  - 2 lives: Orange (danger)
  - 1 life: Red (critical)
- **Visual Feedback**: Red screen flash on incorrect guesses
- **Persistent Messages**: Error messages display temporarily for user awareness

### User Experience
- **Category Selection Menu**: Interactive menu to choose word themes
- **Hover Effects**: Keyboard buttons highlight on mouse hover
- **Game Over Screens**: Clear win/lose messages with restart options
- **Sound Effects**: Audio feedback for correct/incorrect guesses and game events
- **Smooth Performance**: 60 FPS rendering with proper event handling

## Prerequisites

- Python 3.11 or newer
- `pygame` package

## Setup

1. Open a terminal in the project root:

```powershell
cd c:\Users\okeyn\Downloads\Knot-Today-K-master\Knot-Today-K-master
```

2. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install the dependency:

```powershell
python -m pip install pygame
```

## How to Play

1. Launch the game by running `main.py`
2. Select a word category from the menu or choose "Random"
3. Guess letters by clicking the virtual keyboard buttons or typing on your physical keyboard
4. Each incorrect guess reduces your lives and advances the hangman drawing
5. Win by guessing all letters in the word before running out of lives
6. Lose when the hangman drawing is complete (6 incorrect guesses)

## Controls

- **Mouse**: Click on letter buttons or menu options
- **Keyboard**: Type letters A-Z to make guesses
- **ESC**: Return to menu or exit
- **SPACE**: Restart game (on game over screen)

## Run the game

```powershell
cd c:\Users\okeyn\Downloads\Knot-Today-K-master\Knot-Today-K-master
python main.py
```

Or if using the virtual environment from the parent directory:

```powershell
& c:\Users\okeyn\Downloads\Knot-Today-K-master\.venv\Scripts\python.exe main.py
```

## VS Code setup

- Use the Python interpreter at `.venv\Scripts\python.exe`
- If `pygame` still shows unresolved, reload VS Code or restart the Python language server

## Project Structure

- `main.py`: Game entry point and main loop
- `game_logic.py`: Core game mechanics
- `renderer.py`: Pygame rendering and UI components
- `game_state.py`: Game state management
- `sound_manager.py`: Audio system
- `settings.py`: Configuration constants
- `theme.py`: Color palette and styling
- `ui.py`: User interface components
- `utils.py`: Helper functions
- `data/words.json`: Word bank with categorized words
- `assets/sounds/`: Sound effect files

## Notes

- The game loads the word bank from `data/words.json`
- Be sure to run `main.py` from the project root so the relative path `data/words.json` resolves correctly
- Sound files should be placed in `assets/sounds/` directory

## Technical Details

Built with Python and Pygame, featuring:
- Object-oriented architecture
- Event-driven programming
- JSON-based data storage
- Modular component design
- 60 FPS smooth rendering
