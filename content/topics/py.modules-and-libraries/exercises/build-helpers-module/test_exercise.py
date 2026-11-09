import importlib
import io
import sys
from contextlib import redirect_stdout

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_mean_and_spread():
    """mean_of([2, 4, 9]) is 5 and spread([2, 4, 9]) is 7."""
    assert function("mean_of")([2, 4, 9]) == 5
    assert function("mean_of")([1, 2]) == 1.5
    assert function("spread")([2, 4, 9]) == 7
    assert function("spread")([3]) == 0


def test_pick():
    """pick always returns one of the items."""
    pick = function("pick")
    for _ in range(20):
        assert pick(["a", "b", "c"]) in ["a", "b", "c"]
    assert pick(["only"]) == "only"


def test_dice():
    """dice(10, 6) is ten whole numbers from 1 to 6; dice(0, 6) is []."""
    dice = function("dice")
    rolls = dice(10, 6)
    assert isinstance(rolls, list) and len(rolls) == 10
    for roll in rolls:
        assert isinstance(roll, int) and 1 <= roll <= 6
    assert dice(0, 6) == []
    assert dice(3, 1) == [1, 1, 1]


def test_docstrings():
    """Every helper has a docstring."""
    for name in ("mean_of", "spread", "pick", "dice"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_import_is_quiet():
    """Importing the file prints nothing: main runs only when the file is run directly."""
    sys.modules.pop("solution", None)
    out = io.StringIO()
    with redirect_stdout(out):
        importlib.import_module("solution")
    assert out.getvalue() == ""


def test_program():
    """Run directly, the file prints Mean: 5 and Spread: 7."""
    assert run() == "Mean: 5\nSpread: 7\n"
