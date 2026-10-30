# Sudoku project guidance

## Structure
- `starter/app.py`: Flask routes, current-game state, board validation, locked-cell enforcement.
- `starter/sudoku_logic.py`: Sudoku generation, solving, and unique-solution checks.
- `starter/templates/index.html`: accessible game markup and completion dialog.
- `starter/static/main.js`: board interaction, hints, checking, timer, theme, and local leaderboard.
- `starter/static/styles.css`: responsive light/dark presentation and board states.
- `starter/test_app.py`: pytest coverage for generator and Flask endpoints.

## Development
Run from `starter` with `.venv\\Scripts\\python.exe app.py` and open `http://127.0.0.1:5000`.
Run tests with `.venv\\Scripts\\python.exe -m pytest -v`.
Use Python functions and clear snake_case names in the backend; use camelCase in JavaScript. Keep changes focused and avoid adding dependencies without a clear need.

## Game invariants
Every generated puzzle must be a valid Sudoku with exactly one solution. Original clues and server-recorded hinted cells are immutable. Hints may fill exactly one currently empty, non-clue, non-hinted cell with the solution value. Validate request shapes and values before using them, and return friendly JSON errors for malformed or invalid requests.

The client must not claim completion until every board cell equals the solution and the backend reports `complete`. Timer state must reset per puzzle, stop once on successful completion, and never create duplicate intervals. Leaderboard entries come only from successful completion, are validated before use, sorted by time, limited to ten, and stored under `sudoku-top-10` in localStorage. Corrupt localStorage must fall back safely. Theme preference is stored under `sudoku-theme` without resetting the active puzzle.

After changes, run the full pytest suite and perform a browser smoke test for the affected interaction. Do not weaken existing tests or claim unperformed visual evidence.
