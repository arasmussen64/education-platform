from checks import run


def lines(height):
    return run(f"{height}\n").splitlines()


def test_rows():
    """The triangle has one row per unit of height: *, **, *** for a height of 3."""
    printed = lines(3)
    assert printed[:3] == ["*", "**", "***"], f"Your program printed:\n{printed}"
    printed = lines(1)
    assert printed[:1] == ["*"], f"For a height of 1, your program printed:\n{printed}"


def test_one_line_per_row():
    """Each row is on one line: a height of 3 prints exactly 4 lines, including the count."""
    for height in (3, 4):
        printed = lines(height)
        assert len(printed) == height + 1, (
            f"For a height of {height}, your program printed {len(printed)} lines:\n{printed}"
        )


def test_count():
    """The last line counts the stars: Stars: 6 for a height of 3, Stars: 10 for 4."""
    assert lines(3)[-1] == "Stars: 6", f"Your program printed:\n{lines(3)}"
    assert lines(4)[-1] == "Stars: 10", f"Your program printed:\n{lines(4)}"
    assert lines(1)[-1] == "Stars: 1", f"Your program printed:\n{lines(1)}"
