from checks import function, run


def test_the_output():
    """Prints the two orders and the small case."""
    printed = run()
    assert printed == 'rows 2048\ncolumns 16384\n8\n', f"Your program printed:\n{printed}"


def test_the_threshold():
    """On a 16 by 16 matrix by columns, a 15-line cache misses every element and a 16-line one misses once per line; by rows one line is enough."""
    misses = function("misses")
    assert misses((16, 16), "columns", 15) == 256 and misses((16, 16), "columns", 16) == 32
    assert misses((16, 16), "rows", 1) == 32
