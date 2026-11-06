"""Regenerate scenarios/*/expected.json from the current harness.

Only do this after changing the harness on purpose, and review the diff
before committing: these files are the contract that both CPython and
Pyodide must meet.

Usage (from the repository root):
    python -m uv run python harness/tests/update_expected.py
"""

import json

from scenario_runner import SCENARIOS, run_scenario, scenario_names


def main() -> None:
    for name in scenario_names():
        folder = SCENARIOS / name
        report = run_scenario(folder)
        text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        # newline="\n" keeps LF line endings on Windows too (see .gitattributes).
        (folder / "expected.json").write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {name}/expected.json")


if __name__ == "__main__":
    main()
