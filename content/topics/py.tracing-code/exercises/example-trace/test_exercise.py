from checks import run, run_with


def test_as_written():
    """Prints 13 3: the if branch adds the bonus."""
    assert run() == "13 3\n"


def test_small_total():
    """With total starting at 5, the else branch runs instead: 5 0."""
    assert run_with({"total": 5}) == "5 0\n"
