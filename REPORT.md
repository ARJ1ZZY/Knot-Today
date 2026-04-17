# Knot-Today-K: Hangman Game Report

## Project Overview

**Knot-Today-K** is a modern implementation of the classic Hangman word-guessing game, built with Python and Pygame. The game features a polished graphical user interface with category-based word selection, visual feedback systems, and progressive difficulty indicators.

## Key Features

### Game Mechanics
- **Word Categories**: Choose from various word categories (animals, countries, etc.) loaded from JSON data
- **Lives System**: 6 lives with progressive visual warnings
- **Input Methods**: Mouse-click keyboard buttons or physical keyboard input
- **Game States**: Win/lose detection with restart functionality

### Visual Design
- **Hangman Graphics**: ASCII-style drawing with color-coded progression
- **Responsive Layout**: Centered hangman, positioned answer display, and organized keyboard
- **Color-Coded Lives**:
  - 4+ lives: White (normal)
  - 3 lives: Yellow (caution)
  - 2 lives: Orange (danger)
  - 1 life: Red (critical)
- **Visual Feedback**: Red screen flash on incorrect guesses
- **Persistent Messages**: Error messages display for 1.5 seconds

### User Experience Enhancements
- **Category Selection Menu**: Interactive menu to choose word categories
- **Hover Effects**: Keyboard buttons highlight on mouse hover
- **Game Over Screens**: Clear win/lose messages with restart prompts
- **Smooth Rendering**: 60 FPS with proper event handling

## UI Improvements Made

### Layout Adjustments
- **Centered Hangman**: Moved from left side to screen center for better balance
- **Answer Display Positioning**: Relocated above keyboard area to prevent overlap
- **Keyboard Organization**: 
  - Three rows: QWERTYUIOP, ASDFGHJKL, ZXCVBNM
  - Last row (ZXCVBNM) centered for visual appeal
  - Increased spacing between answer area and keyboard

### Visual Feedback Systems
- **Error Flash**: 0.5-second red overlay on incorrect letter guesses
- **Progressive Color Coding**: Hangman and lives counter change colors as lives decrease
- **Message Persistence**: Warning labels remain visible for user awareness

### Color Scheme
```python
COLORS = {
    "bg_dark": (25, 25, 25),
    "bg_medium": (35, 35, 35),
    "accent": (0, 255, 200),
    "text_primary": (220, 220, 220),
    "text_dim": (150, 150, 150),
    "error": (255, 80, 80),
    "success": (80, 255, 150),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "button": (50, 50, 50),
    "button_hover": (70, 70, 70),
    "button_text": (200, 200, 200)
}
```

## Code Architecture

### Core Files
- **`main.py`**: Entry point, game loop, and category menu
- **`renderer.py`**: Pygame rendering engine with UI components
- **`game_logic.py`**: Core game mechanics and state management
- **`utils.py`**: Helper functions for word loading and screen clearing
- **`settings.py`**: Configuration constants (screen size, fonts, etc.)
- **`theme.py`**: Color palette and visual styling

### Class Structure
- **`PygameRenderer`**: Handles all graphical rendering and user input
  - Drawing methods for hangman, text, buttons, and overlays
  - Event handling for mouse and keyboard input
  - Visual feedback timers and state management

### Data Structure
- **Word Bank**: JSON file with categorized word lists
- **Game State**: Dictionary containing lives, display word, guessed letters, etc.

## Technical Implementation

### Rendering Pipeline
1. Clear screen with background color
2. Draw red flash overlay (if active)
3. Render lives counter with appropriate color
4. Draw hangman figure with color coding
5. Display current word progress
6. Show guessed letters list
7. Render interactive keyboard buttons
8. Display error messages (if any)
9. Show game over overlay (if applicable)

### Event Handling
- **Mouse Events**: Button clicks and hover detection
- **Keyboard Events**: Letter input and special keys (ESC, SPACE)
- **Quit Events**: Window close handling

### Performance Considerations
- 60 FPS cap for smooth animation
- Efficient surface blitting for text and graphics
- Minimal redraws with proper dirty rectangle management

## Installation and Usage

### Prerequisites
- Python 3.11+
- Pygame library

### Setup
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install pygame
```

### Running the Game
```bash
python main.py
```

### Controls
- **Mouse**: Click letter buttons or category options
- **Keyboard**: Type letters directly, ESC to quit, SPACE to restart
- **Window**: Close button to exit

## Development Notes

### UI Evolution
The interface evolved from a basic terminal-style layout to a polished graphical experience:
- Initial: Left-aligned hangman with overlapping elements
- Improved: Centered layout with proper spacing and visual hierarchy
- Enhanced: Color-coded feedback and smooth animations

### Code Quality
- Modular design with separate concerns
- Consistent naming conventions
- Comprehensive error handling
- Extensible theme system

### Future Enhancements
- Sound effects for feedback
- Animation for hangman drawing
- High score tracking
- Multiplayer modes
- Custom word list support

## Conclusion

Knot-Today-K demonstrates effective game development practices with a focus on user experience. The combination of clean code architecture, responsive design, and progressive visual feedback creates an engaging and intuitive hangman game that stands out from basic implementations.