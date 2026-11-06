from checks import run, run_with


def test_fourteen_eggs():
    """Prints 2 full boxes and 2 spare eggs."""
    printed = run()
    assert printed == "2 full boxes and 2 spare eggs\n", (
        f"Your program printed:\n{printed}"
    )


def test_any_number_of_eggs():
    """Works for any number of eggs, not just 14."""
    printed = run_with({"eggs": 20})
    assert printed == "3 full boxes and 2 spare eggs\n", (
        "With 20 eggs it should print 3 full boxes and 2 spare eggs. "
        f"It printed:\n{printed}"
    )
