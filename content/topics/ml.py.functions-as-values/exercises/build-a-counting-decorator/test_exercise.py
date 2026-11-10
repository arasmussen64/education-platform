from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints 9, 16, then 2."""
    assert run() == "9\n16\n2\n"


def test_counts_any_function():
    """counted wraps a two-argument function, returns its results, and counts from 0."""
    counted = function("counted")

    def add(a, b):
        return a + b

    add = counted(add)
    assert add.count == 0
    assert add(2, 3) == 5
    assert add(10, 5) == 15
    assert add.count == 2


def test_each_decorated_function_has_its_own_count():
    """Two decorated functions keep separate counts."""
    counted = function("counted")
    first = counted(lambda: "a")
    second = counted(lambda: "b")
    first()
    first()
    assert first.count == 2
    assert second.count == 0
