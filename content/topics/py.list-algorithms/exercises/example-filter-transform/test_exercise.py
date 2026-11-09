from checks import run, run_with


def test_scores():
    """Prints the passing scores, the doubled scores, the sorted list, and its top three."""
    assert run() == (
        "[72, 88, 91, 60]\n[144, 90, 176, 182, 120]\n[45, 60, 72, 88, 91]\n[72, 88, 91]\n"
    )


def test_other_scores():
    """Works for a list of two scores as well."""
    assert run_with({"scores": [1, 70]}) == "[70]\n[2, 140]\n[1, 70]\n[1, 70]\n"
