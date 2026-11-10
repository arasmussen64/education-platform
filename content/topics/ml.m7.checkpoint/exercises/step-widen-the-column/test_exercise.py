import numpy as np

from checks import function, run


def test_the_output():
    """Prints the four weekly counts and int64."""
    printed = run()
    assert printed == '[140, 350, 700, 840] int64\n', f"Your program printed:\n{printed}"


def test_the_edge():
    """An int8 127 gives 889 and a uint8 255 gives 1785."""
    weekly = function("weekly")
    assert list(weekly(np.array([127], dtype=np.int8))) == [889]
    assert list(weekly(np.array([255], dtype=np.uint8))) == [1785]
