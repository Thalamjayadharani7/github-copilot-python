# Manual QA Report

Date: 2026-11-02
Application: Flask Sudoku at `http://127.0.0.1:5000`
Browser: Integrated Chromium browser

## Summary

The existing project was audited in the real browser before changes were made. The project was not rebuilt or redesigned. The original Hint implementation was reverified and preserved. One confirmed usability defect was found and fixed: arrow-key navigation stopped on locked clue cells. The navigation now skips disabled clue cells.

The earlier confirmed completion-dialog defect was also retained in the final code: `Maybe later` closes the dialog without saving a score.

| Result | Count |
| --- | ---: |
| PASS | 29 |
| FAIL | 0 |
| BLOCKED | 2 |
| NOT VERIFIED | 2 |

The counts are feature-level results, not individual low-level browser assertions.

## A. Application Startup

- Steps: Started the Flask server, opened the home page, waited for the generated board, refreshed the page, and watched browser requests.
- Expected: The page and static assets load without errors and refresh preserves a usable application.
- Actual: Page title was `Sudoku | Daily Grid`; 81 cells rendered; CSS and JavaScript loaded; refresh generated a new usable board.
- Status: **PASS**
- Evidence: `Screenshots/main-light.png`, `Screenshots/main-dark.png`
- Browser console errors: none observed.
- Failed network requests: none observed.
- Flask startup/request errors: none observed in the server output during the audit.

## B. Sudoku Game and Puzzle Generation

- Steps: Selected Easy, Medium, and Hard; generated multiple boards; clicked New Game; inspected clue counts and editable/disabled cells.
- Expected: Easy, Medium, and Hard produce valid boards with the documented clue counts; clues are locked; empty cells are editable; New Game resets state and changes the puzzle.
- Actual: Easy produced 42 clues, Medium 34, Hard 28. Each board had 81 cells. Disabled clue cells had values, editable cells were available, and New Game changed the board and reset the hint count.
- Status: **PASS**
- Evidence: `Screenshots/difficulty-selector.png`, `Screenshots/main-light.png`
- Automated uniqueness support: pytest validates generated solutions and uniqueness across all three difficulties.

## C. Number Input and Validation

- Steps: Entered values in editable cells, entered an invalid character, cleared a value after waiting for async validation, created duplicate values, entered a wrong value, and used Check Puzzle.
- Expected: Invalid characters are rejected; clearing removes the value and stale state; wrong values receive red feedback; duplicates are visibly distinguished; clues remain protected.
- Actual: Invalid characters were rejected. A cleared cell became empty and its stale wrong/duplicate classes were removed after server validation. Wrong values received a light red background and red border. Duplicate conflicts used the existing orange border design and the Check message explicitly reported orange duplicates. Original clues remained disabled.
- Status: **PASS** for the current documented design.
- Evidence: `Screenshots/wrong-answer-red.png`, `Screenshots/duplicate-conflict-border.png`, `Screenshots/errors-and-duplicates.png`
- Note: The checklist wording says red duplicate borders, but the existing project intentionally uses orange duplicate borders and documents that behavior. No design change was made.

## D. Hint Feature

- Steps: Clicked Hint once on a fresh board; inspected the value, class, disabled state, message, and counter; filled one user cell first and repeatedly clicked Hint until no empty cells remained.
- Expected: Exactly one correct empty cell is filled and locked per click; hinted styling is applied; the counter increments once; user values are not overwritten; exhaustion is reported.
- Actual: One click produced one correct value, one disabled `.hinted` cell, the existing green hinted styling, success feedback, and counter `1`. With one user-entered cell protected, 38 hints filled the remaining empty cells; the user value remained unchanged; the next click displayed `There are no more hints available.` and left the count at 38.
- Status: **PASS**
- Evidence: `Screenshots/hints-and-locked-cells.png`, `Screenshots/hinted-cell-green.png`
- Related automated coverage: `test_hints_are_correct_locked_and_not_repeated` and `test_hints_skip_user_filled_cells_and_report_when_exhausted`.

## E. Check Puzzle

- Steps: Checked a board with wrong and duplicate values, checked an incomplete board, and completed an Easy board using 39 real Hint clicks before checking.
- Expected: Feedback distinguishes wrong, duplicate, incomplete, and complete states.
- Actual: Wrong/duplicate feedback displayed the expected message and classes. Incomplete boards reported that empty cells remained. A fully filled board displayed `All answers are correct!` and opened the completion dialog.
- Status: **PASS**
- Evidence: `Screenshots/incomplete-puzzle-feedback.png`, `Screenshots/errors-and-duplicates.png`, `Screenshots/successful-completion.png`

## F. Number Tracking and Note Mode

- Steps: Selected every tracking digit from 1 through 9; used Note Mode on two cells; added and removed a note; exited Note Mode and entered a normal answer.
- Expected: Tracking selects one digit and reports occurrences; notes add/remove independently; normal entry resumes after Note Mode.
- Actual: Each digit selected correctly and reported `count of 9`. Notes displayed `5`, removed back to empty, and displayed `3` in another cell. Normal entry then placed `7` and cleared the note display.
- Status: **PASS**
- Evidence: `Screenshots/number-tracking.png`, `Screenshots/note-mode.png`

## G. Visual Solver

- Steps: Opened and closed the solver panel; used Step; used Play; used Pause; used Reset; compared the player board before and after.
- Expected: The solver preview advances independently and controls work without changing the player board.
- Actual: The panel opened, Step advanced the solver, Play changed to Pause, Pause changed back to Play, Reset returned to Step 0, and the player board remained unchanged.
- Status: **PASS**
- Evidence: `Screenshots/visual-solver.png`

## H. Timer

- Steps: Observed the timer after startup, waited for an increment, clicked New Game, waited again, and refreshed the page.
- Expected: Timer starts, increments, resets for a new game, and starts fresh after refresh because persistence is not implemented.
- Actual: Observed `00:06`, New Game reset to approximately `00:02`, it restarted incrementing, and refresh started at `00:00`.
- Status: **PASS**
- Evidence: `Screenshots/timer-running.png`

## I. Theme

- Steps: Toggled light/dark mode, inspected the label and theme state, refreshed, and inspected the persisted state.
- Expected: Theme changes and persists without changing the active application structure.
- Actual: Both theme states rendered, the accessible label changed, and the selected theme persisted after refresh.
- Status: **PASS**
- Evidence: `Screenshots/main-light.png`, `Screenshots/main-dark.png`, `Screenshots/dark-theme.png`

## J. Completion Dialog and Leaderboard

- Steps: Completed an Easy puzzle with 39 hints; inspected the dialog summary; saved `Manual QA`; refreshed; inserted 11 valid local entries and refreshed; tested Maybe later separately.
- Expected: Completion dialog shows time/difficulty/hints; Save Score stores a valid row; refresh preserves it; display is limited to 10; Maybe later does not save.
- Actual: Dialog showed the completion summary and 39 hints. Save Score created a row containing name, time, difficulty, and hints; refresh preserved it. Eleven injected valid entries rendered as exactly 10 rows. Maybe later closed the dialog with `Score was not saved.` and did not add the entered name.
- Status: **PASS**
- Evidence: `Screenshots/completion-leaderboard.png`, `Screenshots/leaderboard.png`, `Screenshots/successful-completion.png`

## K. Responsive Design

Actual viewport checks:

| Viewport | Board width | Overflow | Result |
| --- | ---: | --- | --- |
| 1366 x 768 | 600px | No | PASS |
| 1280 x 720 | 600px | No | PASS |
| 768 x 1024 | 600px | No | PASS |
| 390 x 844 | 355px | No | PASS |
| 320 x 640 | 285px | No | PASS |

At all sizes the board fit the viewport, controls remained within the page, and no horizontal overflow was observed. Existing mobile screenshots were also inspected.

- Status: **PASS**
- Evidence: `Screenshots/mobile-layout.png`, `Screenshots/mobile-audit.png`, `Screenshots/reference-mobile-layout.png`

## L. Accessibility and Usability

- Steps: Inspected accessible names, labels, roles, live status regions, focus styling, and arrow-key behavior. Tested the arrow handler across a locked clue. Inspected contrast evidence and reduced-motion CSS.
- Expected: Controls have usable names, focus is visible, keyboard navigation can move through the playable grid, and state changes are announced.
- Actual: Buttons, difficulty select, range input, board cells, grid labels, live status regions, and dialog labels were present. Arrow navigation now skips locked clue cells. Existing contrast evidence covers representative light and dark states.
- Status: **PASS** for the tested browser-accessibility surface.
- Evidence: `Screenshots/accessibility-controls.png`, `Screenshots/keyboard-focus.png`, `Screenshots/accessibility-contrast-evidence.png`
- BLOCKED: The integrated browser automation tool did not advance focus with synthetic Tab/Shift+Tab presses, so a complete physical tab-order audit and dialog Tab audit could not be completed.
- NOT VERIFIED: Full NVDA, JAWS, VoiceOver, or formal WCAG certification.

## M. Security and Data Handling

- Steps: Entered invalid values; tested localStorage with a short HTML-like name; tested corrupt leaderboard JSON; tested the Top 10 limit; inspected rendered HTML.
- Expected: Invalid input is rejected, unsafe names are escaped, corrupt storage fails safely, and no unnecessary backend/database changes occur.
- Actual: Invalid cell input was rejected. `<b>x</b>` rendered as escaped text with no `b` element. Corrupt localStorage produced an empty leaderboard safely. Eleven valid entries were limited to ten. The project uses in-memory game state and browser-local leaderboard storage as documented.
- Status: **PASS**
- Evidence: `Screenshots/leaderboard.png`

## Bugs Found and Fixes

1. **Arrow navigation stopped at locked clues.** Confirmed in the browser: ArrowRight from an editable cell immediately before a clue left focus in place. Fixed `focusCell` in `starter/static/main.js` to skip disabled cells. Added a regression contract assertion in `starter/test_app.py`. Retested successfully.
2. **Maybe later saved a score.** This was fixed before this QA pass and retested: the button now closes the dialog without adding a leaderboard entry.

No other confirmed application bugs were found. Playwright click-stability and synthetic Tab behavior were treated as tooling limitations, not application failures.

## Automated Verification

Executed after the final code changes:

```text
pytest -q
14 passed

python -m py_compile app.py sudoku_logic.py
node --check static\main.js
python -m json.tool prompts.json
```

All listed commands passed. The final Git diff was reviewed. The final ZIP was extracted successfully and contained the required source, tests, documentation, and screenshots without Git, virtual environment, cache, or bytecode files.

## Screenshot Inventory

The existing Screenshots folder contains evidence for light theme, dark theme, difficulty, hints, wrong answers, duplicates, timer, completion, incomplete feedback, leaderboard, number tracking, Note Mode, Visual Solver, keyboard focus, accessibility controls, contrast, desktop/mobile layouts, and `final-tests.png`. A historical Copilot conversation screenshot is unavailable and was not fabricated.

## Remaining Limitations

- Full screen-reader testing is NOT VERIFIED.
- Formal WCAG certification is NOT VERIFIED; representative contrast checks are documented.
- Complete physical Tab/Shift+Tab and keyboard-dialog testing is BLOCKED by the browser automation tool behavior.
- The duplicate visual state is intentionally orange in the existing design, while one checklist phrase requested red-only duplicate borders.

## Submission Readiness

**READY WITH DOCUMENTED LIMITATIONS.** The application starts, the reviewer-reported Hint behavior works in the real browser, all core gameplay and supporting features tested here passed, the confirmed keyboard-navigation defect was fixed, and the automated suite reports 14 passed tests.
