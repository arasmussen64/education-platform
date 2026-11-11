import numpy as np

from checks import function, run

EXPECTED = 'training loss: 0.446 -> 0.187 | converging\nvalidation accuracy after 20 epochs: 0.9 | above 0.6: True\n'


def test_the_output():
    """Prints a converging loss and a validation accuracy well above a third."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_pieces():
    """SGD steps against the gradient by the rate, and accuracy picks the largest logit per row."""
    SGD = function("SGD")
    accuracy = function("accuracy")
    param = np.array([1.0, 2.0])
    SGD(0.5).step([param], [np.array([2.0, -2.0])])
    assert param.tolist() == [0.0, 3.0]
    assert accuracy(np.array([[0.2, 0.8], [0.9, 0.1], [0.4, 0.6]]), np.array([1, 0, 0])) == 2 / 3
