from checks import run


def test_the_books():
    """Prints both books, True, then 722."""
    assert run() == (
        "Book(title='Dune', pages=412, price=9.99)\n"
        "Book(title='The Hobbit', pages=310, price=0.0)\nTrue\n722\n"
    )
