import numpy as np

from checks import function, run

EXPECTED = 'pooling a 4x4: [[4.0, 8.0], [12.0, 16.0]] | cells that get gradient: 4\ngradient check of the parameters: passes | of the input: passes\n'


def test_the_output():
    """Prints four cells and two passes."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_pieces():
    """The pool's gradient lands on the winners only, and the conv's input gradient matches central differences on an asymmetric kernel."""
    MaxPool2D = function("MaxPool2D")
    Conv2D = function("Conv2D")
    pool = MaxPool2D(2)
    pool.forward(np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]]))
    back = pool.backward(np.array([[[[1.0, 2.0], [3.0, 4.0]]]]))
    assert back.tolist() == [[[[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 4.0]]]]
    conv = Conv2D(1, 2, seed=0)
    conv.W[0] = np.array([[1.0, 2.0], [3.0, 4.0]])
    X = np.arange(9.0).reshape(1, 3, 3)
    conv.forward(X)
    grad_in = conv.backward(np.ones((1, 1, 2, 2)))
    assert grad_in[0].tolist() == [[1.0, 3.0, 2.0], [4.0, 10.0, 6.0], [3.0, 7.0, 4.0]]
