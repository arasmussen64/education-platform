from checks import function, run


def call(wrapped, *args):
    """Call a wrapped function. A wrapper with fixed parameters can't take
    another number of arguments; say that plainly instead of crashing."""
    try:
        return wrapped(*args)
    except TypeError as error:
        count = "1 argument" if len(args) == 1 else f"{len(args)} arguments"
        raise AssertionError(
            f"The wrapper should take any number of arguments, but a call with {count} failed: {error}"
        ) from None


def test_the_output():
    """Prints None, then Hello, Ada, then Bye, Bob twice."""
    printed = run()
    assert printed == "None\nHello, Ada\nBye, Bob\nBye, Bob\n", f"Your program printed:\n{printed}"


def test_wraps_any_function():
    """remember wraps a three-argument function and returns its results."""
    remember = function("remember")

    def total(a, b, c):
        return a + b + c

    total = remember(total)
    assert callable(total), "remember should return the wrapper function, not call it."
    got = call(total, 1, 2, 3)
    assert got == 6, f"A wrapped total(1, 2, 3) should still return 6, but it returned {got!r}."


def test_keeps_the_last_result():
    """The wrapper's last attribute starts as None and then holds the latest result."""
    remember = function("remember")
    double = remember(lambda x: x * 2)
    assert hasattr(double, "last"), "remember should return the wrapper, which has a last attribute."
    assert double.last is None, f"Before any call, last should be None, but it is {double.last!r}."
    call(double, 4)
    assert double.last == 8, f"After double(4), last should be 8, but it is {double.last!r}."
    call(double, 10)
    assert double.last == 20, f"After double(10), last should be 20, but it is {double.last!r}."
