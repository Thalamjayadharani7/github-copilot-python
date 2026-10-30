# Rubric audit

The original external rubric was not present in the workspace. The supplied task requirements were audited against the final code and browser behavior.

## Required features

- **PASS** — Easy, Medium, and Hard generation: browser observed 42, 34, and 28 locked clues; pytest covers uniqueness and validity.
- **PASS** — Original clues and hinted cells are locked; backend rejects tampering.
- **PASS** — Hints are correct, non-repeating, counted, green, and locked.
- **PASS** — Check Puzzle distinguishes empty, incorrect, duplicate, and complete states.
- **PASS** — Timer starts, resets, stops on completion, and does not create overlapping intervals.
- **PASS** — Light/dark themes work and theme persistence was verified after refresh.
- **PASS** — Completion dialog shows time, hints, and difficulty; leaderboard save and persistence were verified.
- **PASS** — Responsive layout: board measured 600px at 1920/1366/768 widths, 355px at 390px, and 325px at 360px with no observed overflow.
- **PASS** — Number tracking highlights selected digits and reports occurrences out of nine; correctness remains separate.
- **PASS** — Note Mode adds/removes candidate digits without changing answer values.
- **PASS** — Visual solver uses genuine backtracking steps, Play/Pause, Step, speed, and Reset on a separate board; a full Easy trace completed and the player board remained unchanged until explicitly filled for completion testing.
- **PASS** — Practical accessibility improvements: semantic labels, keyboard arrows, visible focus, live status announcements, reduced-motion CSS, and text/shape error explanations.
- **PASS** — Representative rendered contrast measurements meet AA after fixing the dark primary button: light body 15.12:1, light button 5.36:1, light cell 7.56:1, dark body 15.16:1, dark button 7.56:1, dark cell 10.34:1. Ratios were calculated from Chromium computed colors using WCAG relative luminance.
- **PASS** — `prompts.json` is valid and contains development, debugging, testing, UI, accessibility, security, and code-review categories.

## Verification commands

- **PASS** — `python -m pytest -q`: 13 passed.
- **PASS** — `node --check starter\static\main.js`.
- **PASS** — `python -m py_compile app.py sudoku_logic.py`.
- **PASS** — `python -m json.tool prompts.json`.
- **PASS** — Browser smoke and end-to-end checks executed against `http://127.0.0.1:5000`.
- **PASS** — Browser console/page-error check returned zero errors after the final script and CSS changes.
- **PASS** — Genuine screenshots cover the main themes, difficulty, hints, wrong answers, duplicates, timer, incomplete feedback, leaderboard, tracking, notes, solver, focus, controls, contrast evidence, mobile layout, and completion.

## Not verified or requiring manual tooling

- **NOT VERIFIED** — Formal WCAG 2.1 AA certification and exhaustive contrast coverage for every state/combination; representative states were measured programmatically.
- **NOT VERIFIED** — Full screen-reader testing with NVDA/JAWS/VoiceOver.
- **NOT VERIFIED** — Historical GitHub Copilot conversation screenshot; none was fabricated.
- **NOT VERIFIED** — A terminal-output screenshot named `final-tests.png`; command results are recorded in this audit instead.
- **NOT VERIFIED** — Original rubric-specific score because that rubric file was unavailable.
