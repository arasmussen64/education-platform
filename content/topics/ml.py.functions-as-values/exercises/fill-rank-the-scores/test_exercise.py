from checks import run, run_with


def test_these_scores():
    """Prints ['Bob', 'Cy', 'Ada'], then Bob."""
    printed = run()
    assert printed == "['Bob', 'Cy', 'Ada']\nBob\n", f"Your program printed:\n{printed}"


def test_other_scores():
    """Works for other scores."""
    printed = run_with({"scores": {"Dee": 50, "Eve": 99, "Fay": 75}})
    assert printed == "['Eve', 'Fay', 'Dee']\nEve\n", f"With Dee 50, Eve 99, Fay 75 it should rank Eve, Fay, Dee. It printed:\n{printed}"
