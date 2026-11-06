"""Every scenario must produce exactly its expected.json under CPython.

The web app's tests run the same scenarios under Pyodide, so passing both
means a learner's code gets the same result in the browser and in CI.
"""

import json

import pytest
from scenario_runner import SCENARIOS, run_scenario, scenario_names


@pytest.mark.parametrize("name", scenario_names())
def test_scenario_matches_expected(name: str) -> None:
    folder = SCENARIOS / name
    expected = json.loads((folder / "expected.json").read_text(encoding="utf-8"))
    assert run_scenario(folder) == expected
