import re

import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Everything is fetched from one
# import of the solution, so the classes compare equal across the tests and
# the training at the top of the file runs once per test.


def module():
    fit = function("fit")
    return fit.__globals__


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
    """Prints the five lines: the shapes, a passing gradient check, a run over the bar with the right parameter count, a double evaluation that agrees, and the reading (the two-decimal loss and accuracy may differ with how the masks and batches are drawn)."""
    printed = run().splitlines()
    expected = '(360, 10, 10) (120, 10, 10) [20, 20, 20, 20, 20, 20]\ngradient check: passes\nloss 1.39 -> 0.03 | held-out accuracy 0.97 | at least 0.9: True | 642 parameters\nevaluating twice gives the same answer: True\nthe first held-out image of each symbol reads: + - x / # o\n'.splitlines()
    assert len(printed) == 5 and printed[0] == expected[0] and printed[1] == expected[1] and printed[3] == expected[3]
    assert re.fullmatch(r"loss \d+\.\d\d -> \d+\.\d\d \| held-out accuracy 0\.\d\d \| at least 0.9: True \| 642 parameters", printed[2]), printed[2]
    assert printed[4].startswith(expected[4].split("reads: ")[0] + "reads: ")
    assert sum(a == b for a, b in zip(printed[4].split("reads: ")[1].split(" "), ['+', '-', 'x', '/', '#', 'o'])) >= 5


def test_layer_gradients():
    """Every parameter's gradient and the input gradient of a conv-ReLU-pool-flatten-dense network match central differences."""
    m = module()
    net = m["Sequential"]([m["Conv2D"](2, 3, seed=4), m["ReLU"](), m["MaxPool2D"](2), m["Flatten"](), m["Dense"](18, 3, seed=5)])
    loss = m["SoftmaxCrossEntropy"]()
    rng = np.random.default_rng(6)
    X = rng.standard_normal((3, 8, 8))
    y = rng.integers(0, 3, size=3)
    net.eval()
    loss.forward(net.forward(X), y)
    grad_in = net.backward(loss.backward())
    f = lambda: loss.forward(net.forward(X), y)
    for param, grad in zip(net.parameters(), net.gradients()):
        assert np.abs(grad - numeric(f, param)).max() < 1e-6
    assert np.abs(grad_in - numeric(f, X)).max() < 1e-6
    assert net.forward(X).shape == (3, 3)


def test_loss_and_optimizer():
    """The loss is the mean negative log-probability and stays finite at 1,000; its gradient is probabilities minus one-hot over the batch; Adam's decay pulls an undefended weight towards zero and no decay leaves it."""
    m = module()
    loss = m["SoftmaxCrossEntropy"]()
    logits = np.array([[2.0, 0.0, -1.0], [1000.0, 0.0, 0.0]])
    labels = np.array([1, 0])
    value = loss.forward(logits, labels)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    assert abs(value - (-np.log(probs[0, 1]) - np.log(probs[1, 0])) / 2) < 1e-9 and np.isfinite(value)
    onehot = np.zeros_like(probs)
    onehot[np.arange(2), labels] = 1
    assert np.allclose(loss.backward(), (probs - onehot) / 2)
    still = np.array([1.0, -2.0])
    m["Adam"](0.01).step([still], [np.zeros(2)])
    assert np.allclose(still, [1.0, -2.0])
    pulled = np.array([1.0, -2.0])
    optimizer = m["Adam"](0.01, weight_decay=0.1)
    for _ in range(50):
        optimizer.step([pulled], [np.zeros(2)])
    assert np.abs(pulled).max() < 1.9 and np.sign(pulled).tolist() == [1.0, -1.0]


def test_dropout_and_modes():
    """Training drops about p and scales survivors by 1 / (1 - p); eval passes everything; train() and eval() flip every flag; evaluate measures in eval mode without changing a weight."""
    m = module()
    layer = m["Dropout"](0.25, seed=2)
    X = np.ones((2000, 8))
    dropped = layer.forward(X)
    assert 0.22 < (dropped == 0).mean() < 0.28 and np.allclose(dropped[dropped > 0], 4 / 3)
    assert np.array_equal(layer.backward(np.ones_like(X)) == 0, dropped == 0)
    net = m["Sequential"]([m["Dense"](8, 4, seed=1), layer, m["Dense"](4, 2, seed=2)])
    net.eval()
    assert layer.training is False and np.array_equal(layer.forward(X), X)
    net.train()
    assert layer.training is True
    before = [p.copy() for p in net.parameters()]
    rows = np.random.default_rng(3).standard_normal((20, 8))
    labels = np.random.default_rng(4).integers(0, 2, size=20)
    first = m["evaluate"](net, m["SoftmaxCrossEntropy"](), rows, labels)
    second = m["evaluate"](net, m["SoftmaxCrossEntropy"](), rows, labels)
    assert first == second and layer.training is False
    assert all(np.array_equal(p, b) for p, b in zip(net.parameters(), before))


def test_starts_and_shapes():
    """Weights start random and scaled by the fan-in, biases at zero, no two units alike; the parameter counts follow the formulas."""
    m = module()
    dense = m["Dense"](100, 50, seed=7)
    assert dense.b.tolist() == [0.0] * 50 and 0.07 < dense.W.std() < 0.13 and not np.allclose(dense.W[:, 0], dense.W[:, 1])
    conv = m["Conv2D"](8, 3, seed=8)
    assert conv.b.tolist() == [0.0] * 8 and 0.2 < conv.W.std() < 0.5 and not np.allclose(conv.W[0], conv.W[1])
    assert sum(p.size for p in dense.parameters()) == 5050 and sum(p.size for p in conv.parameters()) == 80
    net = m["Sequential"]([m["Conv2D"](6, 3, seed=1), m["ReLU"](), m["MaxPool2D"](2), m["Flatten"](), m["Dense"](96, 6, seed=2)])
    assert sum(p.size for p in net.parameters()) == 60 + 96 * 6 + 6
    assert net.forward(np.zeros((2, 10, 10))).shape == (2, 6)


def test_the_accuracy_bar():
    """The trained network reads at least nine in ten held-out images, with a history one entry per epoch; the same seeds give the same history; a different data seed gives different images with the same labels; batches shuffle and cover every row once."""
    m = module()
    net, history, X_val, y_val = m["net"], m["history"], m["X_val"], m["y_val"]
    loss = m["SoftmaxCrossEntropy"]()
    net.eval()
    assert (net.forward(X_val).argmax(axis=1) == y_val).mean() >= 0.9
    assert len(history["train_loss"]) == len(history["val_loss"]) == len(history["val_accuracy"]) == 20
    assert history["train_loss"][-1] < history["train_loss"][0]
    X_train, y_train = m["make_symbols"](60, seed=1)
    again = m["Sequential"]([m["Conv2D"](6, 3, seed=1), m["ReLU"](), m["MaxPool2D"](2), m["Flatten"](), m["Dropout"](0.2, seed=5), m["Dense"](96, 6, seed=2)])
    repeat = m["fit"](again, loss, m["Adam"](0.01, weight_decay=1e-4), X_train, y_train, X_val, y_val, epochs=3)
    assert repeat["val_accuracy"] == history["val_accuracy"][:3] and repeat["train_loss"] == history["train_loss"][:3]
    other, other_labels = m["make_symbols"](60, seed=3)
    assert other.shape == X_train.shape and not np.array_equal(other, X_train) and np.array_equal(other_labels, y_train)
    order = np.concatenate(list(m["batches"](100, 32, np.random.default_rng(0))))
    assert sorted(order.tolist()) == list(range(100)) and order.tolist() != list(range(100))
    assert [len(b) for b in m["batches"](100, 32, np.random.default_rng(1))] == [32, 32, 32, 4]
