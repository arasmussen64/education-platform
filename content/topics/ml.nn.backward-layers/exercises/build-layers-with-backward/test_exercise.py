import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


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
    """Prints the four lines."""
    assert run() == '0.9865 (4, 3) [(3, 4), (4,), (4, 2), (2,)]\nTrue\n0.3143 [[-0.17, 0.121, 0.049], [0.055, -0.095, 0.041]]\nTrue 0.3133\n'


def test_dense_and_relu_backward():
    """A dense layer's three gradients and a ReLU's match numeric derivatives of a squared-output loss."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    layer, relu = Dense(3, 2, seed=5), ReLU()
    X = np.random.default_rng(3).standard_normal((4, 3))

    def total():
        return float((relu.forward(layer.forward(X)) ** 2).sum())

    total()
    grad_in = layer.backward(relu.backward(2 * relu.forward(layer.forward(X))))
    assert np.allclose(layer.dW, central(total, layer.W), atol=1e-6)
    assert np.allclose(layer.db, central(total, layer.b), atol=1e-6)
    assert np.allclose(grad_in, central(total, X), atol=1e-6)
    assert layer.gradients()[0] is layer.dW and relu.gradients() == []


def test_sequential_matches_by_hand():
    """Sequential.backward equals the layers' backward calls in reverse, and the gradients line up with the parameters."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    MSELoss = function("MSELoss")
    net = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 4, seed=2), ReLU(), Dense(4, 2, seed=3)])
    X = np.random.default_rng(4).standard_normal((6, 3))
    y = np.random.default_rng(5).standard_normal((6, 2))
    loss = MSELoss()
    loss.forward(net.forward(X), y)
    grad_in = net.backward(loss.backward())
    grad = loss.backward()
    for layer in reversed(net.layers):
        grad = layer.backward(grad)
    assert np.allclose(grad_in, grad)
    assert [g.shape for g in net.gradients()] == [p.shape for p in net.parameters()]


def test_losses():
    """MSE and its gradient match the formulas; softmax cross-entropy matches a hand computation, its gradient is (p - onehot) / n, and logits of 5,000 stay finite."""
    MSELoss = function("MSELoss")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    pred = np.array([[1.0, 2.0], [0.0, -1.0]])
    target = np.array([[0.0, 2.0], [1.0, 1.0]])
    mse = MSELoss()
    assert abs(mse.forward(pred, target) - 1.5) < 1e-12 and np.allclose(mse.backward(), 2 * (pred - target) / 4)
    ce = SoftmaxCrossEntropy()
    logits = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
    labels = np.array([2, 0])
    p = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
    expected = -np.log(p[[0, 1], labels]).mean()
    assert abs(ce.forward(logits, labels) - expected) < 1e-12
    onehot = np.zeros_like(logits)
    onehot[[0, 1], labels] = 1
    assert np.allclose(ce.backward(), (p - onehot) / 2)
    assert np.isfinite(ce.forward(np.array([[5000.0, 5001.0, 4999.0]]), np.array([0])))


def test_gradient_check_catches_a_bug():
    """gradient_check passes a correct network and reports a gap far above 1e-6 for a layer whose backward drops the mask."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    MSELoss = function("MSELoss")
    gradient_check = function("gradient_check")
    X = np.random.default_rng(6).standard_normal((5, 3))
    y = np.random.default_rng(7).standard_normal((5, 2))
    assert gradient_check(Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 2, seed=2)]), MSELoss(), X, y) < 1e-6

    class LeakyBug(ReLU):
        def backward(self, grad_out):
            return grad_out

    assert gradient_check(Sequential([Dense(3, 4, seed=1), LeakyBug(), Dense(4, 2, seed=2)]), MSELoss(), X, y) > 1e-3
