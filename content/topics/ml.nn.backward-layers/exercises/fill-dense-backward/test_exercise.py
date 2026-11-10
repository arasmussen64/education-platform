import numpy as np

from checks import function, run


def central(f, param, h=1e-6):
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
    """Prints the weight and bias gradients, then the input gradient."""
    printed = run()
    assert printed == '[[1.0, 2.5], [1.0, 0.5], [1.0, -1.5]] [1.0, 1.5]\n[[0.5, 1.0, 0.75], [-1.0, 2.0, 0.5]]\n', f"Your program printed:\n{printed}"


def test_against_numeric_gradients():
    """On other weights and a loss that sums the squared outputs, every stored gradient matches a numeric one."""
    Dense = function("Dense")
    layer = Dense(np.array([[0.3, -0.7, 1.1], [0.9, 0.2, -0.4]]), np.array([0.1, -0.2, 0.3]))
    X = np.array([[1.0, -1.0], [2.0, 0.5], [-0.5, 1.5]])

    def total():
        return float((layer.forward(X) ** 2).sum())

    total()
    grad_in = layer.backward(2 * layer.forward(X))
    assert np.allclose(layer.dW, central(total, layer.W), atol=1e-6)
    assert np.allclose(layer.db, central(total, layer.b), atol=1e-6)
    assert np.allclose(grad_in, central(total, X), atol=1e-6)
