import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three lines."""
    assert run() == '[(8, 16), (8, 16), (8, 10)] 746\n[[0.1, 0.0, 0.5], [0.0, 1.2, 0.0]]\nTrue False\n'


def test_dense_by_hand():
    """A hand-set layer gives X @ W + b for a batch, and parameters() is [W, b]."""
    Dense = function("Dense")
    layer = Dense(3, 2)
    layer.W, layer.b = np.array([[1.0, -1.0], [0.0, 2.0], [0.5, 0.5]]), np.array([-0.5, 0.0])
    X = np.array([[1.0, 1.0, 1.0], [2.0, 0.0, -2.0]])
    assert layer.forward(X).tolist() == [[1.0, 1.5], [0.5, -3.0]]
    W, b = layer.parameters()
    assert W is layer.W and b is layer.b


def test_relu():
    """ReLU zeroes negatives, keeps positives and zero, keeps the shape, and has no parameters."""
    ReLU = function("ReLU")
    out = ReLU().forward(np.array([[-2.0, 0.0, 3.5], [1e-9, -1e-9, -100.0]]))
    assert out.tolist() == [[0.0, 0.0, 3.5], [1e-9, 0.0, 0.0]] and ReLU().parameters() == []


def test_sequential_and_counts():
    """A [7, 5, 3] stack matches its layers called one by one, lists four parameters of the right shapes, and counts 58."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    count_parameters = function("count_parameters")
    shapes_through = function("shapes_through")
    stack = Sequential([Dense(7, 5, seed=3), ReLU(), Dense(5, 3, seed=4)])
    X = np.random.default_rng(1).standard_normal((4, 7))
    by_hand = stack.layers[2].forward(stack.layers[1].forward(stack.layers[0].forward(X)))
    assert np.allclose(stack.forward(X), by_hand)
    assert [p.shape for p in stack.parameters()] == [(7, 5), (5,), (5, 3), (3,)]
    assert count_parameters(stack) == 58
    assert shapes_through(stack, X) == [(4, 5), (4, 5), (4, 3)]
    deep = Sequential([Dense(7, 6, seed=1), ReLU(), Dense(6, 6, seed=2), ReLU(), Dense(6, 2, seed=3)])
    assert shapes_through(deep, X) == [(4, 6), (4, 6), (4, 6), (4, 6), (4, 2)] and count_parameters(deep) == 7 * 6 + 6 + 6 * 6 + 6 + 6 * 2 + 2


def test_starting_weights():
    """Two layers with the same seed start identical, different seeds differ, biases are zero, and the scale is about 1 / sqrt(n_in)."""
    Dense = function("Dense")
    a, b, c = Dense(100, 50, seed=7), Dense(100, 50, seed=7), Dense(100, 50, seed=8)
    assert np.array_equal(a.W, b.W) and not np.array_equal(a.W, c.W)
    assert np.array_equal(a.b, np.zeros(50)) and 0.07 < a.W.std() < 0.13
