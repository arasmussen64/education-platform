from checks import function, run


def book():
    return [
        {"price": 50.05, "shares": 100},
        {"price": 50.10, "shares": 200},
        {"price": 50.20, "shares": 400},
    ]


def test_the_printout():
    """Prints that 300 fill now and 200 wait on the book as a bid at 50.10."""
    printed = run()
    expected = "filled 300 now\n200 wait on the book as a bid at 50.10\n"
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_at_the_limit_counts():
    """An ask exactly at the limit price fills: limit_buy(book, 500, 50.10) is 300."""
    limit_buy = function("limit_buy")
    got = limit_buy(book(), 500, 50.10)
    assert got == 300, f"limit_buy(book, 500, 50.10) returned {got}"


def test_never_more_than_wanted():
    """It never fills more than the order asks for: limit_buy(book, 150, 50.20) is 150."""
    limit_buy = function("limit_buy")
    got = limit_buy(book(), 150, 50.20)
    assert got == 150, f"limit_buy(book, 150, 50.20) returned {got}"


def test_limit_below_every_ask():
    """A limit below every ask fills nothing yet: limit_buy(book, 500, 50.00) is 0."""
    limit_buy = function("limit_buy")
    got = limit_buy(book(), 500, 50.00)
    assert got == 0, f"limit_buy(book, 500, 50.00) returned {got}"


def test_limit_above_every_ask():
    """A limit above every ask takes the whole book: limit_buy(book, 1000, 51.00) is 700."""
    limit_buy = function("limit_buy")
    got = limit_buy(book(), 1000, 51.00)
    assert got == 700, f"limit_buy(book, 1000, 51.00) returned {got}"
