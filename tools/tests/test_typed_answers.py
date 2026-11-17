"""How a typed answer is read (ADR-0027). The cases live in typed_cases.json,
which web/src/content/typed.test.ts reads too, so the validator and the page
read every answer the same way."""

import json
from pathlib import Path

import pytest
from typed_answers import default_case, is_slip, normalise

CASES = json.loads((Path(__file__).parent / "typed_cases.json").read_text("utf-8"))


@pytest.mark.parametrize(
    "case", CASES["normalise"], ids=lambda case: f"{case['kind']}:{case['typed']!r}"
)
def test_normalise(case: dict[str, str]) -> None:
    assert normalise(case["typed"], case["kind"], case["case"]) == case["read"]


@pytest.mark.parametrize(
    "case", CASES["slips"], ids=lambda case: f"{case['typed']}~{case['answer']}"
)
def test_is_slip(case: dict[str, object]) -> None:
    assert is_slip(str(case["typed"]), str(case["answer"])) is case["slip"]


def test_a_commands_case_matters_and_a_terms_does_not() -> None:
    assert default_case("command") == "sensitive"
    assert default_case("text") == "insensitive"
