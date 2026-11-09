from checks import function, run


def test_program():
    """Running the program prints The plant is 15 cm tall."""
    got = run()
    assert got == "The plant is 15 cm tall\n", f"Your program printed:\n{got}"


def test_grow_returns():
    """grow(10) returns 15: the new height comes back to the caller."""
    grow = function("grow")
    assert grow(10) == 15, f"grow(10) returned {grow(10)!r}"


def test_report_returns():
    """report(3) returns The plant is 3 cm tall."""
    report = function("report")
    assert report(3) == "The plant is 3 cm tall", f"report(3) returned {report(3)!r}"
