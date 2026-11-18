from checks import function, run

EXPECTED = (
    "sold 200 at 49.95 to B2\n"
    "sold 100 at 49.95 to B4\n"
    "sold 100 at 49.90 to B1\n"
    "left on the book:\n"
    "B1 200 at 49.90\n"
    "B3 500 at 49.80\n"
)


def other_book():
    return [
        {"id": "P", "price": 12.30, "shares": 50},
        {"id": "Q", "price": 12.40, "shares": 70},
        {"id": "R", "price": 12.40, "shares": 30},
        {"id": "T", "price": 12.20, "shares": 400},
    ]


def test_the_report():
    """Sells 400 shares to the three best bids and prints what is left on the book."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_highest_bid_first():
    """On another book, a market sell of 120 shares fills at 12.40 (Q, then R), then 12.30."""
    match_market_sell = function("match_market_sell")
    fills = match_market_sell(other_book(), 120)
    expected = [
        {"id": "Q", "price": 12.40, "shares": 70},
        {"id": "R", "price": 12.40, "shares": 30},
        {"id": "P", "price": 12.30, "shares": 20},
    ]
    assert fills == expected, f"Expected these fills:\n{expected}\nmatch_market_sell returned:\n{fills}"


def test_the_book_afterwards():
    """After that sale the book holds P with 30 shares left, then T untouched."""
    match_market_sell = function("match_market_sell")
    book = other_book()
    match_market_sell(book, 120)
    expected = [
        {"id": "P", "price": 12.30, "shares": 30},
        {"id": "T", "price": 12.20, "shares": 400},
    ]
    assert book == expected, f"Expected the book to be:\n{expected}\nIt was:\n{book}"
