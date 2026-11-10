from checks import function, run


def test_the_output():
    """Prints True True."""
    printed = run()
    assert printed == 'True True\n', f"Your program printed:\n{printed}"


def test_another_function():
    """Finds the line that builds the big list in two functions, with a size above the floats' own bytes."""
    biggest_allocation = function("biggest_allocation")

    def work():
        tiny = [0.0] * 10
        huge = [float(i) for i in range(50_000)]
        return tiny, huge

    line, size = biggest_allocation(work)
    assert line == work.__code__.co_firstlineno + 2 and size > 50_000 * 8

    def other():
        huge = [float(i) for i in range(40_000)]
        tiny = [0.0] * 10
        return huge, tiny

    line, size = biggest_allocation(other)
    assert line == other.__code__.co_firstlineno + 1 and size > 40_000 * 8
