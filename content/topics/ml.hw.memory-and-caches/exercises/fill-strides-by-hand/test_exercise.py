import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three stride tuples."""
    printed = run()
    assert printed == '(32, 8) (20, 4) (24, 8, 2)\n', f"Your program printed:\n{printed}"


def test_against_numpy():
    """Matches NumPy's strides for several shapes and item sizes, including one axis and four."""
    c_strides = function("c_strides")
    for shape in ((7,), (3, 4), (2, 3, 4), (2, 3, 4, 5)):
        for dtype in ("int16", "float32", "float64"):
            assert c_strides(shape, np.dtype(dtype).itemsize) == np.zeros(shape, dtype=dtype).strides
