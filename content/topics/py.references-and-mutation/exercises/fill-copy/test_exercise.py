from checks import run, run_with


def test_original_kept():
    """Prints the original in its own order, then the sorted copy."""
    got = run()
    assert got == "[3, 1, 2]\n[1, 2, 3]\n", f"Your program printed:\n{got}"


def test_other_list():
    """Works for the list [2, 1] as well."""
    got = run_with({"original": [2, 1]})
    assert got == "[2, 1]\n[1, 2]\n", f"With original [2, 1], your program printed:\n{got}"
