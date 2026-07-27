/**
 * Sudoku Game - Frontend Logic
 * Handles UI interactions, game state, timer, leaderboard, and API communication
 */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const gameState = {
    puzzle: null,
    solution: null,
    board: null,
    selectedCell: null,
    timerInterval: null,
    elapsedSeconds: 0,
    gameActive: false,
    difficulty: 'medium'
};

const BOARD_SIZE = 9;
const EMPTY_CELL = 0;

// ============================================================================
// DOM ELEMENTS
// ============================================================================

const elements = {
    board: document.getElementById('sudokuBoard'),
    difficulty: document.getElementById('difficulty'),
    newGameBtn: document.getElementById('newGameBtn'),
    resetBtn: document.getElementById('resetBtn'),
    timer: document.getElementById('timer'),
    checkBtn: document.getElementById('checkBtn'),
    hintBtn: document.getElementById('hintBtn'),
    submitBtn: document.getElementById('submitBtn'),
    statusMessage: document.getElementById('statusMessage'),
    leaderboard: document.getElementById('leaderboard'),
    themeToggle: document.getElementById('themeToggle'),
    winModal: document.getElementById('winModal'),
    modalOverlay: document.getElementById('modalOverlay'),
    playerName: document.getElementById('playerName'),
    saveScoreBtn: document.getElementById('saveScoreBtn'),
    newGameFromWinBtn: document.getElementById('newGameFromWinBtn'),
    finalTime: document.getElementById('finalTime')
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadLeaderboard();
    attachEventListeners();
    showStatus('Click "New Game" to start playing!', 'info');
});

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        elements.themeToggle.textContent = '☀️';
    } else {
        document.body.classList.remove('dark-mode');
        elements.themeToggle.textContent = '🌙';
    }
    localStorage.setItem('theme', theme);
}

elements.themeToggle.addEventListener('click', () => {
    const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
});

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function attachEventListeners() {
    elements.newGameBtn.addEventListener('click', newGame);
    elements.resetBtn.addEventListener('click', resetBoard);
    elements.checkBtn.addEventListener('click', checkBoard);
    elements.hintBtn.addEventListener('click', getHint);
    elements.submitBtn.addEventListener('click', submitBoard);
    elements.difficulty.addEventListener('change', (e) => {
        gameState.difficulty = e.target.value;
    });
    elements.saveScoreBtn.addEventListener('click', saveScore);
    elements.newGameFromWinBtn.addEventListener('click', () => {
        closeWinModal();
        newGame();
    });
}

// ============================================================================
// GAME INITIALIZATION
// ============================================================================

async function newGame() {
    try {
        gameState.difficulty = elements.difficulty.value;
        const response = await fetch('/api/puzzle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty: gameState.difficulty })
        });

        const data = await response.json();
        gameState.puzzle = JSON.parse(JSON.stringify(data.puzzle));
        gameState.solution = JSON.parse(JSON.stringify(data.solution));
        gameState.board = JSON.parse(JSON.stringify(data.puzzle));
        gameState.gameActive = true;
        gameState.elapsedSeconds = 0;
        gameState.selectedCell = null;

        renderBoard();
        startTimer();
        showStatus('New game started! Solve the puzzle.', 'success');
    } catch (error) {
        console.error('Error starting new game:', error);
        showStatus('Error starting new game. Please try again.', 'error');
    }
}

function resetBoard() {
    if (!gameState.gameActive) {
        showStatus('Start a new game first!', 'info');
        return;
    }

    gameState.board = JSON.parse(JSON.stringify(gameState.puzzle));
    gameState.selectedCell = null;
    renderBoard();
    showStatus('Board reset to initial state.', 'info');
}

// ============================================================================
// BOARD RENDERING
// ============================================================================

function renderBoard() {
    elements.board.innerHTML = '';

    for (let row = 0; row < BOARD_SIZE; row++) {
        for (let col = 0; col < BOARD_SIZE; col++) {
            const cell = createCell(row, col);
            elements.board.appendChild(cell);
        }
    }
}

function createCell(row, col) {
    const cell = document.createElement('div');
    cell.className = 'sudoku-cell';
    cell.dataset.row = row;
    cell.dataset.col = col;

    const value = gameState.board[row][col];
    const originalValue = gameState.puzzle[row][col];

    if (originalValue !== EMPTY_CELL) {
        cell.textContent = value;
        cell.classList.add('locked');
    } else if (value !== EMPTY_CELL) {
        cell.textContent = value;
    }

    cell.addEventListener('click', () => selectCell(cell, row, col));
    cell.addEventListener('keydown', (e) => handleKeyInput(e, row, col));

    return cell;
}

function selectCell(cellElement, row, col) {
    if (gameState.puzzle[row][col] !== EMPTY_CELL) return; // Can't edit locked cells

    // Clear previous selection
    if (gameState.selectedCell) {
        gameState.selectedCell.classList.remove('selected');
    }

    gameState.selectedCell = cellElement;
    cellElement.classList.add('selected');
    cellElement.focus();
}

function handleKeyInput(event, row, col) {
    const key = event.key;

    // Allow digits 1-9
    if (/^[1-9]$/.test(key)) {
        event.preventDefault();
        gameState.board[row][col] = parseInt(key);
        renderBoard();
        showStatus('Cell updated.', 'info');
    }
    // Allow Backspace/Delete to clear cell
    else if (key === 'Backspace' || key === 'Delete') {
        event.preventDefault();
        gameState.board[row][col] = EMPTY_CELL;
        renderBoard();
        showStatus('Cell cleared.', 'info');
    }
    // Allow arrow keys for navigation
    else if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
        event.preventDefault();
        navigateCell(key, row, col);
    }
}

function navigateCell(direction, currentRow, currentCol) {
    let newRow = currentRow;
    let newCol = currentCol;

    switch (direction) {
        case 'ArrowUp':
            newRow = (currentRow - 1 + BOARD_SIZE) % BOARD_SIZE;
            break;
        case 'ArrowDown':
            newRow = (currentRow + 1) % BOARD_SIZE;
            break;
        case 'ArrowLeft':
            newCol = (currentCol - 1 + BOARD_SIZE) % BOARD_SIZE;
            break;
        case 'ArrowRight':
            newCol = (currentCol + 1) % BOARD_SIZE;
            break;
    }

    // Skip locked cells
    if (gameState.puzzle[newRow][newCol] === EMPTY_CELL) {
        const nextCell = document.querySelector(`[data-row="${newRow}"][data-col="${newCol}"]`);
        selectCell(nextCell, newRow, newCol);
    }
}

// ============================================================================
// GAME ACTIONS
// ============================================================================

async function checkBoard() {
    if (!gameState.gameActive) {
        showStatus('Start a new game first!', 'info');
        return;
    }

    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: gameState.board })
        });

        const data = await response.json();

        // Clear error highlighting
        document.querySelectorAll('.sudoku-cell.error').forEach(cell => {
            cell.classList.remove('error');
        });

        if (data.valid) {
            showStatus('✓ No conflicts detected!', 'success');
        } else {
            // Highlight error cells
            data.errors.forEach(([row, col]) => {
                const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
                if (cell) cell.classList.add('error');
            });
            showStatus(`✗ Found ${data.errors.length} error(s). Highlighted in red.`, 'error');
        }
    } catch (error) {
        console.error('Error checking board:', error);
        showStatus('Error checking board.', 'error');
    }
}

async function getHint() {
    if (!gameState.gameActive) {
        showStatus('Start a new game first!', 'info');
        return;
    }

    try {
        const response = await fetch('/api/hint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                puzzle: gameState.board,
                solution: gameState.solution
            })
        });

        if (!response.ok) {
            const error = await response.json();
            showStatus(error.error || 'No hints available.', 'info');
            return;
        }

        const data = await response.json();
        gameState.board[data.row][data.col] = data.value;

        renderBoard();

        // Highlight hint cell
        const hintCell = document.querySelector(`[data-row="${data.row}"][data-col="${data.col}"]`);
        if (hintCell) {
            hintCell.classList.add('hint');
            setTimeout(() => hintCell.classList.remove('hint'), 1000);
        }

        showStatus('Hint revealed! One cell filled.', 'success');
    } catch (error) {
        console.error('Error getting hint:', error);
        showStatus('Error getting hint.', 'error');
    }
}

async function submitBoard() {
    if (!gameState.gameActive) {
        showStatus('Start a new game first!', 'info');
        return;
    }

    try {
        const response = await fetch('/api/check-complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: gameState.board })
        });

        const data = await response.json();

        if (data.complete) {
            stopTimer();
            gameState.gameActive = false;
            showStatus('🎉 Puzzle solved! Great job!', 'success');
            showWinModal();
        } else {
            showStatus('✗ Puzzle not yet complete or contains errors.', 'error');
        }
    } catch (error) {
        console.error('Error submitting board:', error);
        showStatus('Error submitting board.', 'error');
    }
}

// ============================================================================
// TIMER
// ============================================================================

function startTimer() {
    if (gameState.timerInterval) clearInterval(gameState.timerInterval);

    gameState.timerInterval = setInterval(() => {
        gameState.elapsedSeconds++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }
}

function updateTimerDisplay() {
    const minutes = Math.floor(gameState.elapsedSeconds / 60);
    const seconds = gameState.elapsedSeconds % 60;
    elements.timer.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// ============================================================================
// LEADERBOARD
// ============================================================================

function loadLeaderboard() {
    const scores = JSON.parse(localStorage.getItem('sudokuScores')) || [];
    displayLeaderboard(scores);
}

function displayLeaderboard(scores) {
    if (scores.length === 0) {
        elements.leaderboard.innerHTML = '<p class="no-scores">No completed games yet. Solve a puzzle to appear here!</p>';
        return;
    }

    let html = '';
    scores.slice(0, 10).forEach((score, index) => {
        const medals = ['🥇', '🥈', '🥉'];
        const medal = medals[index] || `${index + 1}.`;
        const entryClass = index === 0 ? 'first' : index === 1 ? 'second' : index === 2 ? 'third' : '';

        html += `
            <div class="leaderboard-entry ${entryClass}">
                <div class="leaderboard-rank medal">${medal}</div>
                <div class="leaderboard-name">${score.name}</div>
                <div class="leaderboard-difficulty">${score.difficulty}</div>
                <div class="leaderboard-time">${score.time}</div>
            </div>
        `;
    });

    elements.leaderboard.innerHTML = html;
}

function saveScoreToLeaderboard(name, time, difficulty) {
    const scores = JSON.parse(localStorage.getItem('sudokuScores')) || [];
    scores.push({ name, time, difficulty, timestamp: new Date().toISOString() });

    // Sort by time (ascending) and keep top 10
    scores.sort((a, b) => {
        const aTime = timeToSeconds(a.time);
        const bTime = timeToSeconds(b.time);
        return aTime - bTime;
    });

    localStorage.setItem('sudokuScores', JSON.stringify(scores.slice(0, 10)));
    loadLeaderboard();
}

function timeToSeconds(timeString) {
    const [minutes, seconds] = timeString.split(':').map(Number);
    return minutes * 60 + seconds;
}

// ============================================================================
// WIN MODAL
// ============================================================================

function showWinModal() {
    const timeString = formatTime(gameState.elapsedSeconds);
    elements.finalTime.textContent = timeString;
    elements.playerName.value = '';
    elements.winModal.classList.remove('hidden');
    elements.modalOverlay.classList.remove('hidden');
    elements.playerName.focus();
}

function closeWinModal() {
    elements.winModal.classList.add('hidden');
    elements.modalOverlay.classList.add('hidden');
}

function saveScore() {
    const name = elements.playerName.value.trim() || 'Anonymous';
    const time = formatTime(gameState.elapsedSeconds);
    saveScoreToLeaderboard(name, time, gameState.difficulty);
    closeWinModal();
    showStatus(`✓ Score saved! ${name}: ${time}`, 'success');
}

// ============================================================================
// STATUS MESSAGES
// ============================================================================

function showStatus(message, type = 'info') {
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message ${type}`;

    if (type !== 'error') {
        setTimeout(() => {
            elements.statusMessage.classList.add('hidden');
        }, 3000);
    }
}
