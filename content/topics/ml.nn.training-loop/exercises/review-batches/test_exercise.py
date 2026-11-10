import numpy as np

from checks import function, run


def test_the_output():
    """Prints the sizes, the coverage and False."""
    assert run() == '[5, 5, 5, 5, 3] True\nFalse\n'


def test_other_sizes():
    """Twelve rows in batches of 4 give three full batches covering every row; two epochs differ."""
    batches = function("batches")
    rng = np.random.default_rng(9)
    one, two = list(batches(12, 4, rng)), list(batches(12, 4, rng))
    assert [len(index) for index in one] == [4, 4, 4] and sorted(np.concatenate(one).tolist()) == list(range(12))
    assert not np.array_equal(np.concatenate(one), np.concatenate(two))
