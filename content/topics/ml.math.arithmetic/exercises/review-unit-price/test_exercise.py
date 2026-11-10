from checks import run, run_with


def test_this_pack():
    """Prints Per kg: 6.00 for 4.5 and 750 grams."""
    assert run() == "Per kg: 6.00\n"


def test_any_pack():
    """Works for any pack: 3.6 for 450 grams is 8.00 per kg."""
    assert run_with({"pack_price": 3.6, "grams": 450}) == "Per kg: 8.00\n"
