from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_cold():
    """Typing 5 prints Cold."""
    assert run("5\n") == "Cold\n"


def test_hot():
    """Typing 30.5 prints Hot."""
    assert run("30.5\n") == "Hot\n"


def test_mild():
    """Typing 18 prints Mild."""
    assert run("18\n") == "Mild\n"


def test_boundaries():
    """10 and 25 are both Mild: not below 10, not above 25."""
    assert run("10\n") == "Mild\n"
    assert run("25\n") == "Mild\n"
