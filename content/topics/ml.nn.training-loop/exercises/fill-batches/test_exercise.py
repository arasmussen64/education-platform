import numpy as np

from checks import function, run


def test_the_output():
    """Prints the batch sizes, the covered indices and False for a repeated order."""
    printed = run()
    assert printed == '[4, 4, 2] [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\nFalse\n', f"Your program printed:\n{printed}"


def test_other_sizes():
    """Every index appears once per epoch, the last batch is short when needed, and two epochs differ."""
    batches = function("batches")
    rng = np.random.default_rng(5)
    one = list(batches(23, 5, rng))
    two = list(batches(23, 5, rng))
    assert [len(index) for index in one] == [5, 5, 5, 5, 3]
    assert sorted(np.concatenate(one).tolist()) == list(range(23))
    assert not np.array_equal(np.concatenate(one), np.concatenate(two))
    assert [len(index) for index in batches(8, 4, rng)] == [4, 4]
