# Sudoku Refactor Project

## Overview

This project refactors a legacy Python Sudoku application into a polished and interactive game experience. The original application works but is limited in functionality, so the goal is to improve the structure of the codebase and add modern gameplay features such as multiple difficulty levels, timing, hints, validation, and a local leaderboard.

GitHub Copilot is part of the development process for this project. It is used to help with code generation, refactoring suggestions, debugging, and learning unfamiliar patterns during implementation.

## Project Goals

- Refactor the legacy code for better readability and maintainability.
- Improve separation of concerns between game logic, rendering, and interaction handling.
- Add gameplay features expected in a richer Sudoku experience.
- Use GitHub Copilot meaningfully during development and document that usage with prompts and screenshots.

## Features

The final version includes the following improvements:

- **Multiple difficulty levels** (Easy, Medium, Hard)
- **Game timer** with pause/resume
- **Top-10 fastest-times leaderboard** (local storage)
- **Real-time answer checking** with immediate feedback
- **Hint system** - reveals one valid cell
- **Clear grid styling** with 3x3 subgrid visual separation
- **Input validation** - only digits 1-9 allowed
- **Win detection** - automatically detects when puzzle is solved
- **Dark mode toggle**
- **Responsive design** for mobile and desktop

## Project Structure

```
sudoku-project/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── prompts.json               # Copilot prompts used during development
├── static/
│   ├── style.css              # Main stylesheet with dark mode
│   └── script.js              # Client-side game logic
├── templates/
│   └── index.html             # Game interface template
├── tests/
│   └── test_app.py            # Unit and integration tests
└── screenshots/               # Project milestone screenshots
    ├── initial_tests.png
    ├── copilot_test_setup.png
    ├── copilot_unique_solution.png
    ├── copilot_local_storage.png
    ├── copilot_grid_styling.png
    └── standout_suggestion.png
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/madx2702/copilot.git
   cd copilot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Flask development server:
```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

## Running Tests

Run the test suite:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

## How to Play

1. **Select Difficulty**: Choose Easy, Medium, or Hard from the dropdown
2. **Start Game**: Click "New Game" to generate a puzzle
3. **Solve**: Click on empty cells and enter digits 1-9
4. **Check Answer**: Click "Check" to validate your current board state
5. **Get Hint**: Click "Hint" to fill one empty cell with a valid number
6. **Submit**: Click "Submit" when you believe the puzzle is complete
7. **Leaderboard**: Top 10 times are saved and displayed automatically

## Game Rules

Sudoku is played on a 9×9 grid divided into nine 3×3 boxes. Each row, column, and 3×3 box must contain the numbers 1 through 9 without duplicates.

## Copilot Usage

This project demonstrates meaningful use of GitHub Copilot for:
- Generating puzzle algorithms and validation logic
- Creating test structures and edge case coverage
- Implementing frontend features (timer, leaderboard storage, hints)
- Refactoring legacy code into modular functions
- Debugging and optimizing performance

See `prompts.json` for specific Copilot interactions and their outcomes.

## Refactoring Highlights

### Code Improvements
- **Modular functions**: Separated puzzle generation, validation, and rendering
- **Clearer naming**: Replaced ambiguous variable names with descriptive ones
- **DRY principle**: Eliminated duplicated validation and checking logic
- **Separation of concerns**: Game logic lives in Python, UI interactions in JavaScript
- **Comprehensive testing**: Added unit and integration tests for core functionality

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest (Python testing framework)
- **Storage**: Browser localStorage (client-side persistence)

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Known Limitations

- Leaderboard data is stored locally in browser (not synced across devices)
- Puzzle generation uses backtracking algorithm (can be slow on very hard puzzles)
- No multiplayer or online features

## Future Enhancements

- Save game progress to local storage
- Difficulty rating system based on puzzle characteristics
- Sound effects and animations
- Statistics tracking (games played, win rate, etc.)
- Export/import puzzles
- Undo/redo functionality

## License

MIT License - Feel free to use this project for learning and personal use.

## Author

Built as part of the Udacity "Refactoring Legacy Code with Copilot" assignment.
