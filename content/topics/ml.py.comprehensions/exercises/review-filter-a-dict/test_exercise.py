from checks import run, run_with


def test_this_stock():
    """Prints {'pens': 12, 'paper': 40}."""
    assert run() == "{'pens': 12, 'paper': 40}\n"


def test_other_stock():
    """Exactly 3 is not more than 3."""
    assert run_with({"stock": {"a": 3, "b": 4}}) == "{'b': 4}\n"
