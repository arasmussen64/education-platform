import numpy as np

from checks import function, printed, run


def test_the_output():
    """Prints eight bins with a bell of hashes."""
    out = run()
    assert out == '  -4.0 to   -3.0 \n  -3.0 to   -2.0 ##\n  -2.0 to   -1.0 ##############\n  -1.0 to    0.0 ##################################\n   0.0 to    1.0 ##################################\n   1.0 to    2.0 ##############\n   2.0 to    3.0 ##\n   3.0 to    4.0 \n', f"Your program printed:\n{out}"


def test_a_known_sample():
    """Two bins over a sample that splits 75 to 25 print 75 and 25 hashes."""
    histogram = function("histogram")
    sample = np.array([0.1, 0.2, 0.3, 0.6, 0.4, 0.2, 0.9, 0.3])
    out = printed(histogram, sample, np.array([0.0, 0.5, 1.0]))
    assert out == "   0.0 to    0.5 " + "#" * 75 + "\n   0.5 to    1.0 " + "#" * 25 + "\n", out
