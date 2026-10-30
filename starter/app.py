from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': None,
    'hinted': set(),
}

DIFFICULTIES = sudoku_logic.DIFFICULTIES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in DIFFICULTIES:
        return jsonify({'error': 'Choose easy, medium, or hard.'}), 400
    clues = DIFFICULTIES[difficulty]
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['hinted'] = set()
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not valid_board(board):
        return jsonify({'error': 'The board data is invalid. Please try again.'}), 400
    if not respects_locked_cells(board):
        return jsonify({'error': 'Original and hinted cells cannot be changed.'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != sudoku_logic.EMPTY and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    duplicates = duplicate_cells(board)
    complete = not incorrect and not duplicates and all(
        board[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
    return jsonify({'incorrect': incorrect, 'duplicates': duplicates, 'complete': complete})

@app.route('/hint', methods=['POST'])
def hint():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'Start a game before asking for a hint.'}), 400
    if not valid_board(board):
        return jsonify({'error': 'The board data is invalid. Please try again.'}), 400
    if not respects_locked_cells(board):
        return jsonify({'error': 'Original and hinted cells cannot be changed.'}), 400
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] == sudoku_logic.EMPTY and (row, col) not in CURRENT['hinted']:
                CURRENT['hinted'].add((row, col))
                return jsonify({'row': row, 'col': col, 'value': solution[row][col]})
    return jsonify({'error': 'There are no more hints available.'}), 400

def valid_board(board):
    return (
        isinstance(board, list)
        and len(board) == sudoku_logic.SIZE
        and all(isinstance(row, list) and len(row) == sudoku_logic.SIZE for row in board)
        and all(isinstance(value, int) and 0 <= value <= sudoku_logic.SIZE for row in board for value in row)
    )

def respects_locked_cells(board):
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return False
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY and board[row][col] != puzzle[row][col]:
                return False
            if (row, col) in CURRENT['hinted'] and board[row][col] != solution[row][col]:
                return False
    return True

def duplicate_cells(board):
    duplicates = set()

    def inspect_unit(unit):
        cells_by_value = {}
        for row, col in unit:
            value = board[row][col]
            if value:
                cells_by_value.setdefault(value, []).append((row, col))
        for cells in cells_by_value.values():
            if len(cells) > 1:
                duplicates.update(cells)

    for row in range(sudoku_logic.SIZE):
        inspect_unit([(row, col) for col in range(sudoku_logic.SIZE)])
    for col in range(sudoku_logic.SIZE):
        inspect_unit([(row, col) for row in range(sudoku_logic.SIZE)])
    for box in range(sudoku_logic.SIZE):
        start_row = (box // 3) * 3
        start_col = (box % 3) * 3
        inspect_unit([
            (start_row + offset // 3, start_col + offset % 3)
            for offset in range(sudoku_logic.SIZE)
        ])

    return [[row, col] for row, col in sorted(duplicates)]

if __name__ == '__main__':
    app.run(debug=True)