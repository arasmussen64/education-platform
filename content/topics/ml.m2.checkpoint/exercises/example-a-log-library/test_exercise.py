from checks import run


def test_the_walkthrough():
    """Prints 5 lines, the two warnings, and the summary line."""
    assert run() == "5 lines\n['disk 91% full', 'retrying']\nWARN=2 ERROR=1\n"
