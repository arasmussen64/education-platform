import sys

import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def from_solution(name):
    """The learner's function or class called name, from one load of their file.

    function() runs solution.py from the top on every call, and the program
    at the bottom of that file is slow. So the first call here loads the file
    and every later call reuses that copy: the program runs once per Check
    instead of once per test, which keeps the Check inside the browser's
    time limit. The harness forgets the copy before each Check, so no test
    sees an old version of the file.
    """
    loaded = sys.modules.get("solution")
    if loaded is None:
        return function(name)
    found = getattr(loaded, name, None)
    assert callable(found), f"Define a function called {name}."
    return found


def numeric(f, param, h=1e-6):
    grad = np.zeros_like(param)
    for index in np.ndindex(param.shape):
        old = param[index]
        param[index] = old + h
        up = f()
        param[index] = old - h
        down = f()
        param[index] = old
        grad[index] = (up - down) / (2 * h)
    return grad


def test_the_output():
    """Prints the three lines."""
    assert run() == '[0.0, 3.0, 3.0, 0.0] (6, 6) (2, 2)\n(5, 3) True True 151\n0.96\n'


def test_correlate2d():
    """A 2-by-2 kernel by hand, padding that keeps the size, and a stride of 3."""
    correlate2d = from_solution("correlate2d")
    image = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [2.0, 0.0, 1.0]])
    assert correlate2d(image, np.array([[1.0, 2.0], [0.0, -1.0]])).tolist() == [[4.0, -1.0], [2.0, 6.0]]
    padded = correlate2d(image, np.ones((3, 3)), padding=1)
    assert padded.shape == (3, 3) and padded[1, 1] == image.sum() and padded[0, 0] == image[:2, :2].sum()
    assert correlate2d(np.arange(49.0).reshape(7, 7), np.ones((1, 1)), stride=3).tolist() == [[0.0, 3.0, 6.0], [21.0, 24.0, 27.0], [42.0, 45.0, 48.0]]


def test_conv_forward():
    """Each kernel's map is correlate2d of the image with that kernel plus its bias, and the shape is right."""
    Conv2D = from_solution("Conv2D")
    correlate2d = from_solution("correlate2d")
    rng = np.random.default_rng(7)
    X = rng.standard_normal((3, 7, 6))
    conv = Conv2D(5, 2, seed=3)
    conv.b[:] = rng.standard_normal(5)
    maps = conv.forward(X)
    assert maps.shape == (3, 5, 6, 5) and conv.W.shape == (5, 2, 2)
    for n in range(3):
        for q in range(5):
            assert np.allclose(maps[n, q], correlate2d(X[n], conv.W[q]) + conv.b[q])


def test_conv_backward():
    """dW, db and the input gradient agree with central differences on a weighted sum of the maps."""
    Conv2D = from_solution("Conv2D")
    rng = np.random.default_rng(8)
    X = rng.standard_normal((2, 5, 5))
    weights = rng.standard_normal((2, 3, 3, 3))
    conv = Conv2D(3, 3, seed=5)
    conv.forward(X)
    grad_in = conv.backward(weights)
    f = lambda: float((conv.forward(X) * weights).sum())
    assert np.allclose(conv.dW, numeric(f, conv.W), atol=1e-6)
    assert np.allclose(conv.db, numeric(f, conv.b), atol=1e-6)
    assert np.allclose(grad_in, numeric(f, X), atol=1e-6)
    assert conv.parameters()[0] is conv.W and conv.gradients()[0] is conv.dW


def test_pool_and_flatten():
    """Pooling keeps each window's maximum and routes the gradient to the winner; Flatten round-trips."""
    MaxPool2D = from_solution("MaxPool2D")
    Flatten = from_solution("Flatten")
    block = np.array([[[[1.0, 2.0, 5.0, 6.0], [3.0, 4.0, 7.0, 8.0], [9.0, 10.0, 13.0, 14.0], [11.0, 12.0, 15.0, 16.0]]]])
    pool = MaxPool2D(2)
    assert pool.forward(block).tolist() == [[[[4.0, 8.0], [12.0, 16.0]]]]
    back = pool.backward(np.array([[[[1.0, 2.0], [3.0, 4.0]]]]))
    assert back.tolist() == [[[[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 4.0]]]]
    rng = np.random.default_rng(9)
    maps = rng.standard_normal((4, 3, 6, 6))
    flat = Flatten()
    rows = flat.forward(maps)
    assert rows.shape == (4, 108) and np.array_equal(flat.backward(rows), maps)
    assert pool.parameters() == [] and flat.gradients() == []


def test_counts_and_learning():
    """The parameter count follows the formula, the same seeds repeat, and the network reads nine in ten held-out bars."""
    Conv2D = from_solution("Conv2D")
    ReLU = from_solution("ReLU")
    MaxPool2D = from_solution("MaxPool2D")
    Flatten = from_solution("Flatten")
    Dense = from_solution("Dense")
    Sequential = from_solution("Sequential")
    SoftmaxCrossEntropy = from_solution("SoftmaxCrossEntropy")
    make_bars = from_solution("make_bars")
    assert sum(p.size for p in Conv2D(6, 5, seed=1).parameters()) == 6 * 25 + 6
    X_train, y_train = make_bars(100, seed=1)
    X_test, y_test = make_bars(100, seed=2)
    assert X_train.shape == (100, 8, 8) and y_train.tolist() == [0] * 50 + [1] * 50
    assert np.array_equal(make_bars(100, seed=1)[0], X_train) and not np.array_equal(X_test, X_train)
    net = Sequential([Conv2D(4, 3, seed=1), ReLU(), MaxPool2D(2), Flatten(), Dense(36, 2, seed=2)])
    loss = SoftmaxCrossEntropy()
    for step in range(300):
        loss.forward(net.forward(X_train), y_train)
        net.backward(loss.backward())
        for param, grad in zip(net.parameters(), net.gradients()):
            param -= 0.1 * grad
    assert (net.forward(X_test).argmax(axis=1) == y_test).mean() >= 0.9
