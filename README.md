# Knot-Today-K

A Pygame-based Hangman-style game.

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

## Run the game

```powershell
python main.py
```

## VS Code setup

- Use the Python interpreter at `.venv\Scripts\python.exe`
- If `pygame` still shows unresolved, reload VS Code or restart the Python language server

## Notes

- The game loads the word bank from `data/words.json`
- Be sure to run `main.py` from the project root so the relative path `data/words.json` resolves correctly
