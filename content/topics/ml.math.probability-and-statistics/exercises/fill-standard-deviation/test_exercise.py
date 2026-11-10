from checks import run, run_with


def test_these_values():
    """Prints mean 5.0, then spread 2.0."""
    printed = run()
    assert printed == "mean 5.0\nspread 2.0\n", f"Your program printed:\n{printed}"


def test_other_values():
    """Works for any list: [1, 3, 5] has mean 3.0 and spread about 1.63."""
    printed = run_with({"values": [1, 3, 5]})
    assert printed.startswith("mean 3.0\nspread 1.63"), (
        f"With [1, 3, 5] it should print mean 3.0, then spread 1.63.... It printed:\n{printed}"
    )
