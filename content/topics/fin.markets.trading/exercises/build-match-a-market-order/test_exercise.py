from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXPECTED = (
    "100 at 20.05 from S2\n"
    "300 at 20.10 from S1\n"
    "100 at 20.10 from S3\n"
    "average price 20.09\n"
    "left on the book:\n"
    "S3 100 at 20.10\n"
    "S4 500 at 20.25\n"
)


def other_book():
    """A fresh book for each test, since matching changes it."""
    return [
        {"id": "A", "price": 7.50, "shares": 40},
        {"id": "B", "price": 7.40, "shares": 60},
        {"id": "C", "price": 7.45, "shares": 25},
        {"id": "D", "price": 7.40, "shares": 80},
    ]


def test_the_report():
    """Prints the three fills, the average price, and what is left on the book."""
    assert run() == EXPECTED


def test_best_ask():
    """best_ask picks the lowest price, the earlier order on a tie, and None for an empty book."""
    best_ask = function("best_ask")
    book = other_book()
    assert best_ask(book) == {"id": "B", "price": 7.40, "shares": 60}
    assert best_ask(book[2:]) == {"id": "D", "price": 7.40, "shares": 80}
    assert best_ask([{"id": "X", "price": 3.00, "shares": 5}]) == {"id": "X", "price": 3.00, "shares": 5}
    assert best_ask([]) is None


def test_fills_in_price_and_time_order():
    """match_market_buy fills best price first, then the earlier order on a tie."""
    match_market_buy = function("match_market_buy")
    fills = match_market_buy(other_book(), 150)
    assert fills == [
        {"id": "B", "price": 7.40, "shares": 60},
        {"id": "D", "price": 7.40, "shares": 80},
        {"id": "C", "price": 7.45, "shares": 10},
    ]


def test_the_book_afterwards():
    """A used-up order leaves the book, and a partly used one keeps its place with fewer shares."""
    match_market_buy = function("match_market_buy")
    book = other_book()
    match_market_buy(book, 150)
    assert book == [
        {"id": "A", "price": 7.50, "shares": 40},
        {"id": "C", "price": 7.45, "shares": 15},
    ]


def test_more_than_the_book():
    """An order bigger than the whole book takes everything there is and stops."""
    match_market_buy = function("match_market_buy")
    book = other_book()
    fills = match_market_buy(book, 1000)
    assert fills == [
        {"id": "B", "price": 7.40, "shares": 60},
        {"id": "D", "price": 7.40, "shares": 80},
        {"id": "C", "price": 7.45, "shares": 25},
        {"id": "A", "price": 7.50, "shares": 40},
    ]
    assert book == []
