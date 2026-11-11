"""Runs the repository's real lab checker against a prototype lab that lives
outside the repository. Nothing in the repository is written.

    <repo venv python> run_contract.py <repo root> <content dir> <topic> <exercise> [more exercises]

It imports tools/labcheck.py as a library and calls its own test_lab(), so the
contract is the one CI would run: the pristine container must not pass, the
solution must, every wrong fix must fail a check.
"""

import sys
import time
from pathlib import Path

repo, content, topic, *exercises = sys.argv[1:]
sys.path.insert(0, str(Path(repo) / "tools"))

import labcheck  # noqa: E402

failed = False
for exercise in exercises:
    lab = labcheck.load_lab(topic, exercise, content=Path(content))
    started = time.monotonic()
    report = labcheck.test_lab(lab)
    took = time.monotonic() - started
    print(f"-- {report.lab}: {'ok' if report.ok else 'BROKEN'} in {took:.0f} s")
    for problem in report.problems:
        print(f"   - {problem}")
    failed = failed or not report.ok
sys.exit(1 if failed else 0)
