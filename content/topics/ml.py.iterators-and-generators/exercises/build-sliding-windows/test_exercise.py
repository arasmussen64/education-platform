from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three windows of size 3."""
    assert run() == "[[1, 2, 3], [2, 3, 4], [3, 4, 5]]\n"


def test_other_sizes():
    """Size 1 gives each value alone; a list shorter than the size gives nothing."""
    windows = function("windows")
    assert list(windows([7, 8, 9], 1)) == [[7], [8], [9]]
    assert list(windows([1, 2], 3)) == []


def test_one_at_a_time():
    """windows is a generator: next() gives the first window without building the rest."""
    windows = function("windows")
    first = windows([4, 5, 6], 2)
    assert next(first) == [4, 5]
    assert next(first) == [5, 6]
