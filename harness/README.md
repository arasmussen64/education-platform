# Python harness

The small layer of Python that runs a learner's code and an exercise's tests. The same files run in two places, and they must behave identically in both:

- **In the browser,** inside Pyodide, when a learner presses Run or Check.
- **On GitHub,** under CPython, when exercises are validated.

## Files

| File | What it does |
|---|---|
| `checks.py` | What exercise tests use. `run(stdin)` runs the learner's program and returns what it printed. |
| `program.py` | The Run button. Runs the program the way a terminal would, showing prompts and typed input, and returns the output plus a trimmed traceback. |
| `testrunner.py` | The Check button. Finds the `test_…` functions in `test_exercise.py`, runs them, and reports each one as pass, fail or error. |
| `errors.py` | Turns errors into messages that only mention the learner's own file. |

The learner's code is always `solution.py` in the working folder, and the tests are always `test_exercise.py`.

## Scenarios

Each folder in `scenarios/` is a small case: a solution, then either tests (`test_exercise.py`) or input (`stdin.txt`), and an `expected.json`. Both runtimes must produce exactly the expected report:

- **CPython:** `python -m uv run pytest`, run from the repository root.
- **Pyodide:** `npm test`, run in `web/` (`src/python/session.pyodide.test.ts`).

To add a scenario:

1. Create the folder with its `solution.py`, plus `test_exercise.py` or `stdin.txt`.
2. Run `python -m uv run python harness/tests/update_expected.py`.
3. Read the new `expected.json` before committing.

The expected files are a contract. Never regenerate them just to make a failing test pass.

## Rules

- Standard library only, so it runs in Pyodide.
- Harness file names and paths must never appear in messages the learner sees.
- Use the Python minor version that Pyodide bundles, set in `.python-version` at the repository root.
- Scenarios run in a fresh Python process, not inside pytest. pytest rewrites `assert` statements in any `test_*.py` file it imports, which would change the messages.
