import importlib
import io
import sys
from contextlib import redirect_stdout

from checks import function, run


def test_program():
    """Run directly, the file prints the mean, the root and the pick check."""
    got = run()
    assert got == "Mean: 4\nRoot: 5.0\nPick ok: True\n", f"Your program printed:\n{got}"


def test_functions():
    """root(9) is 3.0 and pick(["x"]) is "x"."""
    assert function("root")(9) == 3.0, "root(9) should be 3.0"
    assert function("pick")(["x"]) == "x", 'pick(["x"]) should be "x"'


def test_import_is_quiet():
    """Importing the file prints nothing."""
    sys.modules.pop("solution", None)
    out = io.StringIO()
    with redirect_stdout(out):
        importlib.import_module("solution")
    assert out.getvalue() == "", f"importing printed:\n{out.getvalue()}"
