import numpy as np

from checks import function, run


def test_the_output():
    """The run clears the bar and the modes are right."""
    printed = run()
    assert printed == 'held-out accuracy at least 0.9: True | dropout off after evaluate: True\ndropout on after train: True | evaluating twice gives the same answer: True\n', f"Your program printed:\n{printed}"


def test_the_modes():
    """evaluate leaves dropout off and changes no weight; fit leaves the network in eval mode after its last measurement."""
    fit = function("fit")
    m = fit.__globals__
    layer = m["Dropout"](0.5, seed=1)
    net = m["Sequential"]([m["Dense"](4, 3, seed=1), layer, m["Dense"](3, 2, seed=2)])
    X = np.random.default_rng(2).standard_normal((30, 4))
    y = np.random.default_rng(3).integers(0, 2, size=30)
    loss = m["SoftmaxCrossEntropy"]()
    before = [p.copy() for p in net.parameters()]
    assert m["evaluate"](net, loss, X, y) == m["evaluate"](net, loss, X, y) and layer.training is False
    assert all(np.array_equal(p, b) for p, b in zip(net.parameters(), before))
    history = m["fit"](net, loss, m["Adam"](0.01), X, y, X, y, epochs=2, batch_size=10)
    assert len(history["val_accuracy"]) == 2 and layer.training is False
