from checks import run, run_with


def test_total():
    """Running the program prints 7.5."""
    got = run()
    assert got == "7.5\n", f"Your program printed:\n{got}"


def test_other_prices():
    """With the prices 1, 2 and 3 it prints 6."""
    got = run_with({"prices": [1, 2, 3]})
    assert got == "6\n", f"With prices [1, 2, 3], your program printed:\n{got}"
