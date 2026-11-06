from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_before_and_after():
    """Prints red blue, then blue red."""
    assert run() == "red blue\nblue red\n"


def test_swaps_using_the_names():
    """Swaps any two values, using the names top and bottom."""
    assert run_with({"top": "left", "bottom": "right"}) == "left right\nright left\n"
