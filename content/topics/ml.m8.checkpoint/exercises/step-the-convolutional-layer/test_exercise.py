import numpy as np

from checks import function, run


def test_the_output():
    """Both gradient checks pass."""
    printed = run()
    assert printed == '(3, 4) | gradient check: passes\ninput gradient: passes\n', f"Your program printed:\n{printed}"


def test_by_hand():
    """A 2-by-2 kernel's gradients and the pool's routing on tiny cases, by hand."""
    Conv2D = function("Conv2D")
    MaxPool2D = function("MaxPool2D")
    conv = Conv2D(1, 2, seed=0)
    conv.W[0] = np.array([[1.0, 2.0], [3.0, 4.0]])
    conv.forward(np.arange(9.0).reshape(1, 3, 3))
    grad_in = conv.backward(np.ones((1, 1, 2, 2)))
    assert conv.dW[0].tolist() == [[8.0, 12.0], [20.0, 24.0]] and conv.db.tolist() == [4.0]
    assert grad_in[0].tolist() == [[1.0, 3.0, 2.0], [4.0, 10.0, 6.0], [3.0, 7.0, 4.0]]
    pool = MaxPool2D(2)
    pool.forward(np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]]))
    assert pool.backward(np.array([[[[1.0, 2.0], [3.0, 4.0]]]])).tolist() == [[[[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 4.0]]]]
