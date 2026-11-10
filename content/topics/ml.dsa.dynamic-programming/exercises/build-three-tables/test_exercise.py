from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == "55 2880067194370816120\n3 3 2\n(150, ['stove', 'water', 'book'])\n6 2 -1\n"


def test_fib_500():
    """fib(500) is the 105-digit number starting 139423224561697880."""
    fib = function("fib")
    value = fib(500)
    assert len(str(value)) == 105 and str(value).startswith("139423224561697880") and fib(2) == 1


def test_edit_distance():
    """intention to execution is 5, the distance is symmetric, and identical strings are 0."""
    edit_distance = function("edit_distance")
    assert edit_distance("intention", "execution") == 5
    assert edit_distance("sunday", "saturday") == 3 and edit_distance("saturday", "sunday") == 3
    assert edit_distance("same", "same") == 0


def test_knapsack_beats_greedy():
    """With capacity 10, one item of weight 10 worth 60 loses to two items of weight 5 worth 35 each, and an empty list fits nothing."""
    knapsack = function("knapsack")
    items = [("big", 10, 60), ("left", 5, 35), ("right", 5, 35)]
    assert knapsack(items, 10) == (70, ["left", "right"])
    assert knapsack([], 10) == (0, [])
    assert knapsack(items, 4) == (0, [])


def test_min_coins():
    """9, 6, 5 and 1 make 11 with two coins, not five."""
    min_coins = function("min_coins")
    assert min_coins([9, 6, 5, 1], 11) == 2 and min_coins([2], 3) == -1 and min_coins([2], 0) == 0
