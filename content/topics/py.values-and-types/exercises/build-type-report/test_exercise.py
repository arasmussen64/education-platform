import re
from pathlib import Path

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_three_lines():
    """Prints three lines."""
    assert len(run().splitlines()) == 3


def test_int_line():
    """The first line reports the int 12."""
    assert run().splitlines()[:1] == ["12 is <class 'int'>"]


def test_float_line():
    """The second line reports the float 12.5."""
    assert run().splitlines()[1:2] == ["12.5 is <class 'float'>"]


def test_str_line():
    """The third line reports the text "12"."""
    assert run().splitlines()[2:3] == ["12 is <class 'str'>"]


def test_uses_type():
    """Uses type() to find each type, instead of typing the types out."""
    source = Path("solution.py").read_text(encoding="utf-8")
    assert len(re.findall(r"\btype\s*\(", source)) >= 3
