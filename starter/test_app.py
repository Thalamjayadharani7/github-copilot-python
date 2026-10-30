import sudoku_logic
from app import CURRENT, app


def test_generated_puzzles_have_unique_valid_solutions():
    for difficulty, clues in sudoku_logic.DIFFICULTIES.items():
        puzzle, solution = sudoku_logic.generate_puzzle(clues)

        assert sum(value != sudoku_logic.EMPTY for row in puzzle for value in row) == clues
        assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle)) == 1
        assert all(sorted(row) == list(range(1, 10)) for row in solution)
        assert all(puzzle[row][col] in (0, solution[row][col]) for row in range(9) for col in range(9))
        assert difficulty in sudoku_logic.DIFFICULTIES


def test_new_game_supports_all_difficulties():
    client = app.test_client()

    for difficulty, clues in sudoku_logic.DIFFICULTIES.items():
        response = client.get(f'/new?difficulty={difficulty}')
        data = response.get_json()

        assert response.status_code == 200
        assert data['difficulty'] == difficulty
        assert sum(value != 0 for row in data['puzzle'] for value in row) == clues


def test_new_game_rejects_unknown_difficulty():
    response = app.test_client().get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json()['error']


def test_check_and_hint_use_the_current_game():
    client = app.test_client()
    new_game = client.get('/new?difficulty=easy').get_json()
    puzzle = new_game['puzzle']
    solution = sudoku_logic.deep_copy(CURRENT['solution'])

    board = sudoku_logic.deep_copy(puzzle)
    hint = client.post('/hint', json={'board': board})
    hint_data = hint.get_json()

    assert hint.status_code == 200
    assert board[hint_data['row']][hint_data['col']] == 0
    assert hint_data['value'] in range(1, 10)

    invalid = client.post('/check', json={'board': []})
    assert invalid.status_code == 400

    board[hint_data['row']][hint_data['col']] = hint_data['value']
    assert hint_data['value'] == solution[hint_data['row']][hint_data['col']]
    check = client.post('/check', json={'board': board})
    assert check.status_code == 200
    assert [hint_data['row'], hint_data['col']] not in check.get_json()['incorrect']
    assert check.get_json()['duplicates'] == []
    assert check.get_json()['complete'] is False


def test_hints_are_correct_locked_and_not_repeated():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=hard').get_json()['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    solution = sudoku_logic.deep_copy(CURRENT['solution'])

    first = client.post('/hint', json={'board': board}).get_json()
    first_position = (first['row'], first['col'])
    board[first['row']][first['col']] = first['value']
    assert first['value'] == solution[first['row']][first['col']]

    second_response = client.post('/hint', json={'board': board})
    second = second_response.get_json()
    assert second_response.status_code == 200
    assert (second['row'], second['col']) != first_position

    board[ first_position[0] ][ first_position[1] ] = 0
    modified = client.post('/hint', json={'board': board})
    assert modified.status_code == 400
    assert 'cannot be changed' in modified.get_json()['error']


def test_hint_rejects_changes_to_original_clues():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=easy').get_json()['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    clue = next((row, col) for row in range(9) for col in range(9) if puzzle[row][col] != 0)
    board[clue[0]][clue[1]] = (puzzle[clue[0]][clue[1]] % 9) + 1

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 400
    assert 'cannot be changed' in response.get_json()['error']


def test_check_rejects_changing_or_removing_original_clues():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=medium').get_json()['puzzle']
    clue = next((row, col) for row in range(9) for col in range(9) if puzzle[row][col] != 0)

    changed = sudoku_logic.deep_copy(puzzle)
    changed[clue[0]][clue[1]] = (puzzle[clue[0]][clue[1]] % 9) + 1
    removed = sudoku_logic.deep_copy(puzzle)
    removed[clue[0]][clue[1]] = 0

    changed_response = client.post('/check', json={'board': changed})
    removed_response = client.post('/check', json={'board': removed})

    assert changed_response.status_code == 400
    assert removed_response.status_code == 400
    assert changed_response.get_json()['error'] == removed_response.get_json()['error']


def test_check_accepts_valid_edits_to_unlocked_non_hinted_cells():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=easy').get_json()['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    empty = next((row, col) for row in range(9) for col in range(9) if puzzle[row][col] == 0)
    board[empty[0]][empty[1]] = CURRENT['solution'][empty[0]][empty[1]]

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [empty[0], empty[1]] not in response.get_json()['incorrect']


def test_check_ignores_empty_cells_and_reports_completion_only_for_full_solution():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=easy').get_json()['puzzle']
    solution = sudoku_logic.deep_copy(CURRENT['solution'])
    response = client.post('/check', json={'board': puzzle})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'duplicates': [], 'complete': False}

    complete = client.post('/check', json={'board': solution})
    assert complete.status_code == 200
    assert complete.get_json() == {'incorrect': [], 'duplicates': [], 'complete': True}


def test_check_reports_wrong_non_empty_cells_but_not_empty_cells():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=medium').get_json()['puzzle']
    solution = CURRENT['solution']
    wrong = next((row, col) for row in range(9) for col in range(9) if puzzle[row][col] == 0)
    board = sudoku_logic.deep_copy(puzzle)
    wrong_value = next(value for value in range(1, 10) if value != solution[wrong[0]][wrong[1]])
    board[wrong[0]][wrong[1]] = wrong_value

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [wrong[0], wrong[1]] in response.get_json()['incorrect']
    assert response.get_json()['complete'] is False


def test_check_reports_all_duplicate_cells_in_rows_columns_and_boxes():
    client = app.test_client()
    puzzle = client.get('/new?difficulty=hard').get_json()['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    solution = CURRENT['solution']
    empties = [(row, col) for row in range(9) for col in range(9) if puzzle[row][col] == 0]

    row_pair = next(pair for pair in ((a, b) for a in empties for b in empties if a[0] == b[0] and a != b))
    col_pair = next(pair for pair in ((a, b) for a in empties for b in empties if a[1] == b[1] and a != b))
    box_pair = next(pair for pair in ((a, b) for a in empties for b in empties if (a[0] // 3, a[1] // 3) == (b[0] // 3, b[1] // 3) and a != b))
    for row, col in row_pair + col_pair + box_pair:
        board[row][col] = 9
    response = client.post('/check', json={'board': board})
    duplicate_set = {tuple(cell) for cell in response.get_json()['duplicates']}

    assert response.status_code == 200
    assert all(cell in duplicate_set for cell in row_pair + col_pair + box_pair)
    assert response.get_json()['complete'] is False


def test_page_includes_script_that_locks_prefilled_cells():
    response = app.test_client().get('/')
    script = app.test_client().get('/static/main.js').get_data(as_text=True)
    styles = app.test_client().get('/static/styles.css').get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="sudoku-board"' in response.get_data(as_text=True)
    assert 'input.disabled = true' in script
    assert 'classList.add(\'prefilled\')' in script
    assert 'addDuplicateUnits' in script
    assert 'box-alt' in script
    assert 'Top 10 Fastest Times' in response.get_data(as_text=True)
    assert '.sudoku-cell.duplicate-error' in styles
    assert '.sudoku-cell.wrong-answer' in styles
    assert 'All answers are correct!' in script
    assert 'finished the ${difficulty} puzzle' in script
    assert 'APPRECIATION_QUOTES' in script
    assert "$('appreciation-quote').textContent" in script
    assert 'refreshWrongAnswerHighlights' in script
    assert "fetch('/check'" in script
    assert "input.classList.remove('wrong-answer')" in script
    assert 'Wrong answer' in response.get_data(as_text=True)
    assert 'Duplicate number' in response.get_data(as_text=True)
    assert 'Hinted and locked' in response.get_data(as_text=True)
    assert 'appreciation-quote' in response.get_data(as_text=True)


def test_check_rejects_invalid_board_values():
    app.test_client().get('/new?difficulty=medium')
    board = [[0 for _ in range(9)] for _ in range(9)]
    board[0][0] = 10

    response = app.test_client().post('/check', json={'board': board})

    assert response.status_code == 400
    assert response.get_json()['error']
