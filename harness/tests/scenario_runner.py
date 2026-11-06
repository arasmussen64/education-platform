"""Run one scenario folder through the harness and return its report.

A scenario folder holds solution.py and either test_exercise.py (a Check)
or, optionally, stdin.txt (a Run). expected.json holds the report both
CPython and Pyodide must produce.

Each scenario runs in a fresh, isolated Python process, like the browser
and the content validator do. That matters: inside pytest, files named
test_*.py get their asserts rewritten, which would change the messages.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HARNESS = Path(__file__).resolve().parents[1]
SCENARIOS = HARNESS / "scenarios"

# Runs inside the child process. argv[1] is the harness folder.
_CHILD = """
import json, sys
from pathlib import Path
sys.path[:0] = [sys.argv[1], "."]
import program, testrunner
if Path(testrunner.TEST_FILE).exists():
    report = testrunner.run_tests()
else:
    stdin_file = Path("stdin.txt")
    stdin = stdin_file.read_text(encoding="utf-8") if stdin_file.exists() else ""
    report = program.run_program(stdin)
print(json.dumps(report))
"""


def scenario_names() -> list[str]:
    return sorted(folder.name for folder in SCENARIOS.iterdir() if folder.is_dir())


def run_scenario(folder: Path) -> dict[str, Any]:
    """Copy the scenario into an empty folder and run it there."""
    with tempfile.TemporaryDirectory() as workdir:
        for file in folder.iterdir():
            if file.name != "expected.json":
                shutil.copy(file, workdir)
        completed = subprocess.run(
            [sys.executable, "-I", "-c", _CHILD, str(HARNESS)],
            cwd=workdir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"Scenario {folder.name} crashed:\n{completed.stderr}")
    return json.loads(completed.stdout)
