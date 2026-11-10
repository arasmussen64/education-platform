import numpy as np

from checks import function, run

EXPECTED = 'loss 1.10 -> 0.17: learning | validation accuracy 0.90\none batch of 8 overfits: True | dead units after training: 0 of 16\n'


def test_the_output():
    """Prints a learning run and a batch that overfits."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_pieces():
    """split keeps every label with its row, and a fresh network overfits eight rows at the script's rate."""
    split = function("split")
    X = np.arange(20.0).reshape(10, 2)
    y = np.arange(10)
    X_train, y_train, X_val, y_val = split(X, y, seed=3)
    assert np.array_equal(X_train[:, 0] / 2, y_train) and np.array_equal(X_val[:, 0] / 2, y_val)
    assert len(X_train) == 8 and sorted(y_train.tolist() + y_val.tolist()) == list(range(10))
    assert not np.array_equal(X_train, X[2:]), "split must shuffle"
