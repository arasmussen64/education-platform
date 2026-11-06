"""Run one scenario folder through the harness and return its report.

A scenario folder holds solution.py and either test_exercise.py (a Check)
or, for a Run, optionally stdin.txt (the input typed so far) and seed.txt
(the random seed). expected.json holds the report both CPython and Pyodide
must produce.

Each scenario runs in a fresh, isolated Python process (harness/cli.py),
like the browser and the content validator do. That matters: inside pytest,
files named test_*.py get their asserts rewritten, which would change the
messages.
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
CLI = HARNESS / "cli.py"


def scenario_names() -> list[str]:
    return sorted(folder.name for folder in SCENARIOS.iterdir() if folder.is_dir())


def run_scenario(folder: Path) -> dict[str, Any]:
    """Copy the scenario into an empty folder and run it there."""
    with tempfile.TemporaryDirectory() as workdir:
        for file in folder.iterdir():
            if file.name != "expected.json":
                shutil.copy(file, workdir)
        work = Path(workdir)
        if (work / "test_exercise.py").exists():
            command = ["check", workdir]
        else:
            command = ["run", workdir]
            if (work / "stdin.txt").exists():
                command += ["--stdin", (work / "stdin.txt").read_text("utf-8")]
            if (work / "seed.txt").exists():
                command += ["--seed", (work / "seed.txt").read_text().strip()]
        completed = subprocess.run(
            [sys.executable, "-I", str(CLI), *command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"Scenario {folder.name} crashed:\n{completed.stderr}")
    return json.loads(completed.stdout)
