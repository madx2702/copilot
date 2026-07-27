"""Test suite for Sudoku game application.

This module contains unit and integration tests for puzzle generation,
validation, solving, and API endpoints.
"""

import pytest
import json
from app import (
    app,
    is_valid,
    solve_board,
    generate_puzzle,
    check_board,
    is_complete_and_valid,
    get_hint
)
import copy


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_board():
    """Return a sample incomplete Sudoku board."""
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]


@pytest.fixture
def complete_valid_board():
    """Return a completely solved, valid Sudoku board."""
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]


@pytest.fixture
def invalid_board():
    """Return an invalid Sudoku board with duplicates."""
    return [
        [5, 5, 0, 0, 7, 0, 0, 0, 0],  # Duplicate 5 in row
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]


# ============================================================================
# TESTS: BOARD VALIDATION
# ============================================================================

class TestBoardValidation:
    """Tests for is_valid function."""

    def test_valid_placement_empty_row(self, sample_board):
        """Test valid number placement in empty cell."""
        board = copy.deepcopy(sample_board)
        assert is_valid(board, 0, 2, 1) is True

    def test_invalid_placement_duplicate_row(self, sample_board):
        """Test invalid placement due to duplicate in row."""
        board = copy.deepcopy(sample_board)
        assert is_valid(board, 0, 2, 5) is False  # 5 already in row

    def test_invalid_placement_duplicate_column(self, sample_board):
        """Test invalid placement due to duplicate in column."""
        board = copy.deepcopy(sample_board)
        assert is_valid(board, 5, 0, 5) is False  # 5 already in column

    def test_invalid_placement_duplicate_box(self, sample_board):
        """Test invalid placement due to duplicate in 3x3 box."""
        board = copy.deepcopy(sample_board)
        assert is_valid(board, 1, 2, 5) is False  # 5 already in box

    def test_valid_placement_all_constraints(self, sample_board):
        """Test valid placement satisfying all constraints."""
        board = copy.deepcopy(sample_board)
        # Find a valid number for position (2, 0)
        for num in range(1, 10):
            if is_valid(board, 2, 0, num):
                assert True
                return
        assert False, "No valid number found"


# ============================================================================
# TESTS: BOARD CHECKING
# ============================================================================

class TestBoardChecking:
    """Tests for check_board function."""

    def test_valid_partial_board(self, sample_board):
        """Test checking a valid partial board."""
        board = copy.deepcopy(sample_board)
        is_valid_board, errors = check_board(board)
        assert is_valid_board is True
        assert errors == []

    def test_invalid_board_duplicate_row(self, invalid_board):
        """Test detection of duplicate in row."""
        board = copy.deepcopy(invalid_board)
        is_valid_board, errors = check_board(board)
        assert is_valid_board is False
        assert len(errors) > 0

    def test_valid_complete_board(self, complete_valid_board):
        """Test checking a complete valid board."""
        board = copy.deepcopy(complete_valid_board)
        is_valid_board, errors = check_board(board)
        assert is_valid_board is True
        assert errors == []


# ============================================================================
# TESTS: BOARD COMPLETION
# ============================================================================

class TestBoardCompletion:
    """Tests for is_complete_and_valid function."""

    def test_incomplete_board(self, sample_board):
        """Test incomplete board returns False."""
        board = copy.deepcopy(sample_board)
        assert is_complete_and_valid(board) is False

    def test_complete_valid_board(self, complete_valid_board):
        """Test complete valid board returns True."""
        board = copy.deepcopy(complete_valid_board)
        assert is_complete_and_valid(board) is True

    def test_complete_invalid_board(self, invalid_board):
        """Test complete invalid board (with duplicates) returns False."""
        # Fill the entire board to make it complete but invalid
        board = copy.deepcopy(invalid_board)
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    board[i][j] = 1  # Fill with 1 (will create duplicates)

        assert is_complete_and_valid(board) is False


# ============================================================================
# TESTS: PUZZLE GENERATION
# ============================================================================

class TestPuzzleGeneration:
    """Tests for generate_puzzle function."""

    def test_puzzle_generation_easy(self):
        """Test generation of easy puzzle."""
        puzzle = generate_puzzle('easy')
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert all(0 <= cell <= 9 for row in puzzle for cell in row)

    def test_puzzle_generation_medium(self):
        """Test generation of medium puzzle."""
        puzzle = generate_puzzle('medium')
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_puzzle_generation_hard(self):
        """Test generation of hard puzzle."""
        puzzle = generate_puzzle('hard')
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_puzzle_has_empty_cells(self):
        """Test that generated puzzle has empty cells."""
        puzzle = generate_puzzle('medium')
        empty_count = sum(1 for row in puzzle for cell in row if cell == 0)
        assert empty_count > 0

    def test_puzzle_has_initial_cells(self):
        """Test that generated puzzle has initial cells filled."""
        puzzle = generate_puzzle('easy')
        filled_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert filled_count > 0


# ============================================================================
# TESTS: BOARD SOLVING
# ============================================================================

class TestBoardSolving:
    """Tests for solve_board function."""

    def test_solve_valid_board(self, sample_board):
        """Test solving a valid board."""
        board = copy.deepcopy(sample_board)
        has_unique, count = solve_board(board, count_only=True)
        # Most puzzles have one solution, but we're just testing it can solve
        assert count > 0

    def test_solve_complete_board(self, complete_valid_board):
        """Test solving already complete board."""
        board = copy.deepcopy(complete_valid_board)
        has_unique, count = solve_board(board, count_only=True)
        # Complete board should count as one solution
        assert count >= 1


# ============================================================================
# TESTS: HINT SYSTEM
# ============================================================================

class TestHintSystem:
    """Tests for get_hint function."""

    def test_hint_returns_valid_cell(self, sample_board, complete_valid_board):
        """Test hint returns a valid empty cell from puzzle."""
        puzzle = copy.deepcopy(sample_board)
        solution = copy.deepcopy(complete_valid_board)

        hint = get_hint(puzzle, solution)
        assert hint is not None
        row, col, value = hint
        assert 0 <= row < 9
        assert 0 <= col < 9
        assert 1 <= value <= 9
        assert puzzle[row][col] == 0  # Cell should be empty

    def test_hint_none_when_complete(self, complete_valid_board):
        """Test hint returns None when no empty cells."""
        puzzle = copy.deepcopy(complete_valid_board)
        solution = copy.deepcopy(complete_valid_board)

        hint = get_hint(puzzle, solution)
        assert hint is None


# ============================================================================
# TESTS: API ENDPOINTS
# ============================================================================

class TestAPIEndpoints:
    """Tests for Flask API endpoints."""

    def test_index_route(self, client):
        """Test GET / returns HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Sudoku' in response.data

    def test_puzzle_endpoint_easy(self, client):
        """Test POST /api/puzzle with easy difficulty."""
        response = client.post('/api/puzzle',
                               json={'difficulty': 'easy'},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data
        assert 'solution' in data
        assert len(data['puzzle']) == 9
        assert len(data['solution']) == 9

    def test_puzzle_endpoint_medium(self, client):
        """Test POST /api/puzzle with medium difficulty."""
        response = client.post('/api/puzzle',
                               json={'difficulty': 'medium'},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data

    def test_puzzle_endpoint_hard(self, client):
        """Test POST /api/puzzle with hard difficulty."""
        response = client.post('/api/puzzle',
                               json={'difficulty': 'hard'},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data

    def test_validate_endpoint_valid(self, client, complete_valid_board):
        """Test POST /api/validate with valid board."""
        response = client.post('/api/validate',
                               json={'board': complete_valid_board},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
        assert data['errors'] == []

    def test_validate_endpoint_invalid(self, client, invalid_board):
        """Test POST /api/validate with invalid board."""
        response = client.post('/api/validate',
                               json={'board': invalid_board},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert len(data['errors']) > 0

    def test_check_complete_endpoint_incomplete(self, client, sample_board):
        """Test POST /api/check-complete with incomplete board."""
        response = client.post('/api/check-complete',
                               json={'board': sample_board},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['complete'] is False

    def test_check_complete_endpoint_complete(self, client, complete_valid_board):
        """Test POST /api/check-complete with complete board."""
        response = client.post('/api/check-complete',
                               json={'board': complete_valid_board},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['complete'] is True

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete game flow."""

    def test_complete_game_flow(self, client):
        """Test complete game flow from puzzle generation to submission."""
        # 1. Generate puzzle
        response = client.post('/api/puzzle',
                               json={'difficulty': 'easy'},
                               content_type='application/json')
        assert response.status_code == 200
        puzzle_data = json.loads(response.data)
        solution = puzzle_data['solution']

        # 2. Validate the generated puzzle is solvable
        response = client.post('/api/validate',
                               json={'board': solution},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True

        # 3. Check if complete
        response = client.post('/api/check-complete',
                               json={'board': solution},
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['complete'] is True
