from checks import run, run_with


def test_program():
    """Prints 100, then 70, 85, 90 and 100 on their own lines."""
    got = run()
    assert got == "100\n70\n85\n90\n100\n", f"Your program printed:\n{got}"


def test_other_scores():
    """With the scores 1 and 2 to start, it prints 100, 1, 2, 100."""
    got = run_with({"scores": [1, 2]})
    assert got == "100\n1\n2\n100\n", f"With scores [1, 2], your program printed:\n{got}"
