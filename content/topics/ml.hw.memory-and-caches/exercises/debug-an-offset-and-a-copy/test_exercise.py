import numpy as np

from checks import function, run

EXPECTED = '48 == 48\n[0. 0. 0. 0.] 4.0\n'


def test_the_output():
    """Prints the matching offsets and a zeroed first row."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_shapes():
    """The offset matches NumPy's strides on a 5 by 7 float32 array, and clearing works on a 2 by 2 int32 array."""
    byte_offset = function("byte_offset")
    clear_top_row = function("clear_top_row")
    a = np.zeros((5, 7), dtype=np.float32)
    assert byte_offset(a.shape, a.itemsize, (3, 6)) == 3 * a.strides[0] + 6 * a.strides[1]
    b = np.ones((2, 2), dtype=np.int32)
    clear_top_row(b)
    assert b.tolist() == [[0, 0], [1, 1]]
