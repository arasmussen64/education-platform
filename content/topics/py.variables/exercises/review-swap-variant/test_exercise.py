from checks import run, run_with

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_prints_swapped():
    """Prints the values swapped: 2 1."""
    assert run() == "2 1\n"


def test_swaps_any_values():
    """Swaps any two values, using the names p and q."""
    assert run_with({"p": "a", "q": "b"}) == "b a\n"
