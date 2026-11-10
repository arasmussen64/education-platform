import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 60 150], then 2."""
    printed = run()
    assert printed == "[ 60 150]\n2\n", f"Your program printed:\n{printed}"


def test_other_sales():
    """Works for three shops and two days: totals per shop, and the best day's position."""
    shop_totals = function("shop_totals")
    best_day = function("best_day")
    sales = np.array([[5, 1], [1, 1], [0, 9]])
    assert shop_totals(sales).tolist() == [6, 2, 9]
    assert best_day(sales) == 1
