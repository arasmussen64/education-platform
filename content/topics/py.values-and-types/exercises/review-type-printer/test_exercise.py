import re
from pathlib import Path

from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_types_in_order():
    """Shows int, then float, then str, one per line."""
    assert run().splitlines() == ["<class 'int'>", "<class 'float'>", "<class 'str'>"]


def test_uses_type():
    """Uses type() to find each type, instead of typing the types out."""
    source = Path("solution.py").read_text(encoding="utf-8")
    assert len(re.findall(r"\btype\s*\(", source)) >= 3
