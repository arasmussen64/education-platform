# Python harness

The small layer of Python that runs a learner's code and an exercise's tests. The same files run in two places, and they must behave identically in both:

- **In the browser,** inside Pyodide, when a learner presses Run or Check.
- **On GitHub,** under CPython, when exercises are validated.

## Files

| File            | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `checks.py`     | What exercise tests use. `run(stdin)` runs the learner's program and returns what it printed. `run_with(values)` does the same with some names starting at other values, so a test can check the code works with its names rather than with retyped values. `function(name)` loads the learner's function of that name (failing with a plain "Define a function called ..." when it's missing, swallowing anything the file prints while loading), and `printed(f, *args)` returns what a call prints, for testing functions that print. |
| `program.py`    | The Run button. Runs the program the way a terminal would, showing prompts and typed input, and returns the output plus a trimmed traceback. When the program wants more input than it was given, it stops and reports `waiting_for_input`, so the app can ask the learner and run it again. `seed` keeps random choices the same across those re-runs.                                                                                                                                                                                  |
| `testrunner.py` | The Check button. Finds the `test_…` functions in `test_exercise.py`, runs them, and reports each one as pass, fail or error.                                                                                                                                                                                                                                                                                                                                                                                                            |
| `tracer.py`     | The Step through button ([ADR-0022](../docs/decisions/0022-step-through.md)). Runs the program exactly as `program.py` does, under Python's trace hook, and records a step for each line about to run, each call, each return and each error: the running calls with their variables as short text, and how much output had been printed. 300 steps at most; values cut at 60 characters.                                                                                                                                                |
| `errors.py`     | Turns errors into messages that only mention the learner's own file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `cli.py`        | Runs one folder through the harness and prints the report as JSON. The content validator and the scenario tests use it, in a fresh Python process. It isn't bundled into the web app.                                                                                                                                                                                                                                                                                                                                                    |

A note on `checks.py`: `function(name)` runs `solution.py` from the top on every call. A test file whose solution is slow to load (one that trains a network as it loads, say) should load it once per Check instead; see `from_solution` in the ML build tests, for example `content/topics/ml.nn.convolution/exercises/build-a-convolutional-layer/test_exercise.py`, and _Time limits_ in [content/README.md](../content/README.md).

The learner's code is always `solution.py` in the working folder, and the tests are always `test_exercise.py`.

## Scenarios

Each folder in `scenarios/` is a small case: a `solution.py`, then either tests (`test_exercise.py`) or, for a Run, optional input (`stdin.txt`) and random seed (`seed.txt`), plus an `expected.json`. An empty `trace.txt` makes it a Step through instead of a Run, and the expected report is then every recorded step. Both runtimes must produce exactly the expected report:

- **CPython:** `python -m uv run pytest`, run from the repository root.
- **Pyodide:** `npm test`, run in `web/` (`src/python/session.pyodide.test.ts`). The same run also checks every ready exercise's reference solution in Pyodide (`src/content/content.pyodide.test.ts`).

To add a scenario:

1. Create the folder with its `solution.py`, plus `test_exercise.py`, or (optionally) `stdin.txt` and `seed.txt`, or an empty `trace.txt` for a Step through.
2. Run `python -m uv run python harness/tests/update_expected.py`.
3. Read the new `expected.json` before committing.

The expected files are a contract. Never regenerate them just to make a failing test pass.

## Rules

- Standard library only, so it runs in Pyodide, plus the packages a topic declares with `packages:` in its `topic.yaml` (NumPy so far, [ADR-0023](../docs/decisions/0023-packages-in-both-runtimes.md)): Pyodide ships them, the app loads them on first use, and the root `pyproject.toml` pins the same version for CPython.
- Harness file names and paths must never appear in messages the learner sees.
- Use the Python minor version that Pyodide bundles, pinned by `requires-python` in the root `pyproject.toml`. There's deliberately no `.python-version` file: Cloudflare's build would spot it and install Python for nothing.
- Scenarios run in a fresh Python process, not inside pytest. pytest rewrites `assert` statements in any `test_*.py` file it imports, which would change the messages.
- Tests may create files (`Path("x.txt").write_text(...)`), and programs may read and write files, all in the working folder; the `check-files` scenario pins that both runtimes agree. Only `solution.py` and `test_exercise.py` are ever copied in, so a data file must be made by the test or by the program itself.
