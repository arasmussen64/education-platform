from checks import run


def test_bad_then_good():
    """Typing abc, then 21, prints Not a whole number. and then Double: 42."""
    got = run("abc\n21\n")
    assert got == "Not a whole number.\nDouble: 42\n", f"Your program printed:\n{got}"


def test_two_bad():
    """Typing x, y, then 5, prints the message twice and then Double: 10."""
    got = run("x\ny\n5\n")
    assert got == "Not a whole number.\nNot a whole number.\nDouble: 10\n", (
        f"Your program printed:\n{got}"
    )


def test_good_first():
    """Typing 8 prints Double: 16 straight away."""
    got = run("8\n")
    assert got == "Double: 16\n", f"Your program printed:\n{got}"
