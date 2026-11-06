# Python harness

The small layer of Python that runs a learner's code and an exercise's tests. The same files run in two places, and they must behave identically in both:

- **In the browser,** inside Pyodide, when a learner presses Run or Check.
- **On GitHub,** under CPython, when exercises are validated.

## Files

| File | What it does |
|---|---|
| `checks.py` | What exercise tests use. `run(stdin)` runs the learner's program and returns what it printed. `run_with(values)` does the same with some names starting at other values, so a test can check the code works with its names rather than with retyped values. |
| `program.py` | The Run button. Runs the program the way a terminal would, showing prompts and typed input, and returns the output plus a trimmed traceback. When the program wants more input than it was given, it stops and reports `waiting_for_input`, so the app can ask the learner and run it again. `seed` keeps random choices the same across those re-runs. |
| `testrunner.py` | The Check button. Finds the `test_…` functions in `test_exercise.py`, runs them, and reports each one as pass, fail or error. |
| `errors.py` | Turns errors into messages that only mention the learner's own file. |
| `cli.py` | Runs one folder through the harness and prints the report as JSON. The content validator and the scenario tests use it, in a fresh Python process. It isn't bundled into the web app. |

The learner's code is always `solution.py` in the working folder, and the tests are always `test_exercise.py`.

## Scenarios

Each folder in `scenarios/` is a small case: a `solution.py`, then either tests (`test_exercise.py`) or, for a Run, optional input (`stdin.txt`) and random seed (`seed.txt`), plus an `expected.json`. Both runtimes must produce exactly the expected report:

- **CPython:** `python -m uv run pytest`, run from the repository root.
- **Pyodide:** `npm test`, run in `web/` (`src/python/session.pyodide.test.ts`).

To add a scenario:

1. Create the folder with its `solution.py`, plus `test_exercise.py` or (optionally) `stdin.txt` and `seed.txt`.
2. Run `python -m uv run python harness/tests/update_expected.py`.
3. Read the new `expected.json` before committing.

The expected files are a contract. Never regenerate them just to make a failing test pass.

## Rules

- Standard library only, so it runs in Pyodide.
- Harness file names and paths must never appear in messages the learner sees.
- Use the Python minor version that Pyodide bundles, pinned by `requires-python` in the root `pyproject.toml`. There's deliberately no `.python-version` file: Cloudflare's build would spot it and install Python for nothing.
- Scenarios run in a fresh Python process, not inside pytest. pytest rewrites `assert` statements in any `test_*.py` file it imports, which would change the messages.
