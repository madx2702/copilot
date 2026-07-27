"""Sudoku game application with Flask backend.

This module provides the Flask application and puzzle generation/validation logic
for an interactive Sudoku game. It demonstrates refactored, modular code that
separates concerns between business logic and presentation.
"""

from flask import Flask, render_template, request, jsonify
import random
import copy
from typing import List, Tuple, Optional

app = Flask(__name__)


# ============================================================================
# PUZZLE GENERATION AND VALIDATION
# ============================================================================

def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if placing num at (row, col) violates Sudoku rules.
    
    Args:
        board: 9x9 grid with 0 representing empty cells
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to place (1-9)
        
    Returns:
        True if placement is valid, False otherwise
    """
    # Check row
    if num in board[row]:
        return False
    
    # Check column
    if num in [board[i][col] for i in range(9)]:
        return False
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    
    return True


def solve_board(board: List[List[int]], count_only: bool = False) -> Tuple[bool, int]:
    """Solve a Sudoku board using backtracking algorithm.
    
    Args:
        board: 9x9 grid with 0 representing empty cells
        count_only: If True, counts solutions instead of finding just one
        
    Returns:
        Tuple of (solved: bool, solution_count: int)
    """
    solutions = [0]
    
    def backtrack():
        if solutions[0] > 1 and count_only:
            return  # Early exit if we found more than one solution
        
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            backtrack()
                            board[row][col] = 0
                    return
        
        solutions[0] += 1
    
    board_copy = copy.deepcopy(board)
    backtrack()
    return solutions[0] == 1, solutions[0]


def generate_puzzle(difficulty: str = 'medium') -> List[List[int]]:
    """Generate a new Sudoku puzzle with a unique solution.
    
    Args:
        difficulty: 'easy', 'medium', or 'hard' determines number of empty cells
        
    Returns:
        9x9 grid representing the puzzle (0 = empty cell)
    """
    # Difficulty levels: number of cells to remove
    difficulty_map = {
        'easy': 40,
        'medium': 50,
        'hard': 60
    }
    
    cells_to_remove = difficulty_map.get(difficulty, 50)
    
    # Generate complete valid board
    board = [[0] * 9 for _ in range(9)]
    
    # Fill diagonal 3x3 boxes (they don't interfere with each other)
    for box in range(3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[box * 3 + i][box * 3 + j] = nums[i * 3 + j]
    
    # Solve to complete the board
    board_copy = copy.deepcopy(board)
    solve_board(board_copy, count_only=False)
    board = board_copy
    
    # Remove cells while maintaining unique solution
    removed = 0
    attempts = 0
    max_attempts = cells_to_remove * 10
    
    while removed < cells_to_remove and attempts < max_attempts:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        
        if board[row][col] != 0:
            num = board[row][col]
            board[row][col] = 0
            
            # Check if puzzle still has unique solution
            board_copy = copy.deepcopy(board)
            has_unique, count = solve_board(board_copy, count_only=True)
            
            if has_unique:
                removed += 1
            else:
                board[row][col] = num  # Restore if solution not unique
        
        attempts += 1
    
    return board


def check_board(board: List[List[int]]) -> Tuple[bool, List[Tuple[int, int]]]:
    """Check if current board state is valid (no conflicts).
    
    Args:
        board: 9x9 grid
        
    Returns:
        Tuple of (is_valid: bool, error_cells: list of (row, col) with conflicts)
    """
    errors = []
    
    for row in range(9):
        for col in range(9):
            if board[row][col] != 0:
                num = board[row][col]
                board[row][col] = 0  # Temporarily remove
                
                if not is_valid(board, row, col, num):
                    errors.append((row, col))
                
                board[row][col] = num  # Restore
    
    return len(errors) == 0, errors


def is_complete_and_valid(board: List[List[int]]) -> bool:
    """Check if board is completely filled and valid.
    
    Args:
        board: 9x9 grid
        
    Returns:
        True if board is solved correctly, False otherwise
    """
    # Check if all cells are filled
    for row in board:
        if 0 in row:
            return False
    
    # Check if valid
    is_valid_board, _ = check_board(copy.deepcopy(board))
    return is_valid_board


def get_hint(puzzle: List[List[int]], solution: List[List[int]]) -> Optional[Tuple[int, int, int]]:
    """Get a hint by revealing one empty cell from the solution.
    
    Args:
        puzzle: Current board state
        solution: Solved board
        
    Returns:
        Tuple of (row, col, value) for the hint cell, or None if no empty cells
    """
    empty_cells = [(i, j) for i in range(9) for j in range(9) if puzzle[i][j] == 0]
    
    if not empty_cells:
        return None
    
    row, col = random.choice(empty_cells)
    return (row, col, solution[row][col])


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main game page."""
    return render_template('index.html')


@app.route('/api/puzzle', methods=['POST'])
def get_puzzle():
    """Generate and return a new puzzle.
    
    Request JSON:
        {"difficulty": "easy"|"medium"|"hard"}
        
    Response JSON:
        {"puzzle": 9x9 grid, "solution": 9x9 grid}
    """
    data = request.get_json()
    difficulty = data.get('difficulty', 'medium')
    
    puzzle = generate_puzzle(difficulty)
    solution = copy.deepcopy(puzzle)
    solve_board(solution, count_only=False)
    
    return jsonify({
        'puzzle': puzzle,
        'solution': solution
    })


@app.route('/api/validate', methods=['POST'])
def validate():
    """Check if current board state is valid.
    
    Request JSON:
        {"board": 9x9 grid}
        
    Response JSON:
        {"valid": bool, "errors": list of (row, col) with conflicts}
    """
    data = request.get_json()
    board = data.get('board')
    
    is_valid_board, errors = check_board(board)
    
    return jsonify({
        'valid': is_valid_board,
        'errors': errors
    })


@app.route('/api/check-complete', methods=['POST'])
def check_complete():
    """Check if board is completely and correctly solved.
    
    Request JSON:
        {"board": 9x9 grid}
        
    Response JSON:
        {"complete": bool}
    """
    data = request.get_json()
    board = data.get('board')
    
    complete = is_complete_and_valid(board)
    
    return jsonify({
        'complete': complete
    })


@app.route('/api/hint', methods=['POST'])
def hint():
    """Get a hint for the current puzzle.
    
    Request JSON:
        {"puzzle": 9x9 grid, "solution": 9x9 grid}
        
    Response JSON:
        {"row": int, "col": int, "value": int} or {"error": str}
    """
    data = request.get_json()
    puzzle = data.get('puzzle')
    solution = data.get('solution')
    
    hint_data = get_hint(puzzle, solution)
    
    if hint_data is None:
        return jsonify({'error': 'No empty cells to reveal'}), 400
    
    row, col, value = hint_data
    return jsonify({
        'row': row,
        'col': col,
        'value': value
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
