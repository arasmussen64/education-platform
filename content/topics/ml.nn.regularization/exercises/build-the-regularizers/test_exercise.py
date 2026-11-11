import sys

import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Every test takes what it needs
# from one load of the solution (its training runs as it loads).


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


def test_the_output():
    """Prints the four lines (the dropout run's last number may differ with how its mask is drawn; the plain and decayed runs may not)."""
    printed = run().splitlines()
    expected = 'overfitting 0.478 2.115\nholding 0.386 drifting up 0.571\n28 48 0.478 48\n0.5 1.0\n'.splitlines()
    assert len(printed) == 4 and printed[0] == expected[0] and printed[2] == expected[2] and printed[3] == expected[3]
    assert printed[1].startswith('holding 0.386 ') and printed[1].split()[2] in ("holding", "drifting")


def test_dropout_modes():
    """Training drops about p and scales survivors by 1 / (1 - p), backward uses the same mask, eval passes everything through, Sequential flips the modes, and evaluate measures with dropout off, giving the same answer twice."""
    fit = from_solution("fit")
    Dropout, Sequential = (fit.__globals__[name] for name in ("Dropout", "Sequential"))
    layer = Dropout(0.25, seed=2)
    X = np.ones((2000, 8))
    out = layer.forward(X)
    assert 0.22 < (out == 0).mean() < 0.28 and np.allclose(out[out > 0], 4 / 3)
    assert np.array_equal(layer.backward(np.ones_like(X)) == 0, out == 0)
    net = Sequential([layer])
    net.eval()
    assert layer.training is False and np.array_equal(net.forward(X), X)
    net.train()
    assert layer.training is True
    evaluate, loss = fit.__globals__["evaluate"], fit.__globals__["SoftmaxCrossEntropy"]()
    rows = np.random.default_rng(3).standard_normal((40, 8))
    labels = np.random.default_rng(4).integers(0, 8, size=40)
    first = evaluate(net, loss, rows, labels)
    assert layer.training is False and first == evaluate(net, loss, rows, labels)


def test_weight_decay_shrinks():
    """With a zero data gradient, Adam with decay pulls a weight towards zero; without decay it stays."""
    Adam = from_solution("fit").__globals__["Adam"]
    still = np.array([1.0, -2.0])
    Adam(0.01).step([still], [np.zeros(2)])
    assert np.allclose(still, [1.0, -2.0])
    pulled = np.array([1.0, -2.0])
    optimizer = Adam(0.01, weight_decay=0.1)
    for _ in range(50):
        optimizer.step([pulled], [np.zeros(2)])
    assert np.abs(pulled).max() < 1.9 and np.sign(pulled).tolist() == [1.0, -1.0]


def test_early_stopping_restores():
    """With a patience of 10 the run stops 10 epochs after its best, the history is that long, and the restored weights give the best validation loss."""
    fit = from_solution("fit")
    Dense, ReLU, Sequential, SoftmaxCrossEntropy, Adam, make_blobs, evaluate = (fit.__globals__[name] for name in ("Dense", "ReLU", "Sequential", "SoftmaxCrossEntropy", "Adam", "make_blobs", "evaluate"))
    X_train, y_train = make_blobs(20, seed=1, spread=1.8)
    X_val, y_val = make_blobs(100, seed=2, spread=1.8)
    net = Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU(), Dense(64, 3, seed=3)])
    loss = SoftmaxCrossEntropy()
    history = fit(net, loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300, patience=10)
    assert history["stopped_at"] == history["best_epoch"] + 10 and len(history["val_loss"]) == history["stopped_at"]
    assert abs(evaluate(net, loss, X_val, y_val)[0] - min(history["val_loss"])) < 1e-9


def test_overfitting_and_a_cure():
    """The plain run's validation loss more than doubles from its low; with decay 0.03 it holds; the same seeds repeat exactly."""
    fit = from_solution("fit")
    Dense, ReLU, Sequential, SoftmaxCrossEntropy, Adam, make_blobs, read_fit = (fit.__globals__[name] for name in ("Dense", "ReLU", "Sequential", "SoftmaxCrossEntropy", "Adam", "make_blobs", "read_fit"))
    X_train, y_train = make_blobs(20, seed=1, spread=1.8)
    X_val, y_val = make_blobs(100, seed=2, spread=1.8)

    def net():
        return Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU(), Dense(64, 3, seed=3)])

    plain = fit(net(), SoftmaxCrossEntropy(), Adam(0.01), X_train, y_train, X_val, y_val, epochs=200)
    assert read_fit(plain) == "overfitting" and plain["train_loss"][-1] < 0.1
    decayed = fit(net(), SoftmaxCrossEntropy(), Adam(0.01, weight_decay=0.03), X_train, y_train, X_val, y_val, epochs=200)
    assert read_fit(decayed) == "holding" and decayed["val_loss"][-1] < plain["val_loss"][-1]
    again = fit(net(), SoftmaxCrossEntropy(), Adam(0.01), X_train, y_train, X_val, y_val, epochs=200)
    assert again["val_loss"] == plain["val_loss"]
    assert read_fit({"val_loss": [1.0, 0.5, 0.55]}) == "holding" and read_fit({"val_loss": [1.0, 0.5, 0.6]}) == "drifting up" and read_fit({"val_loss": [1.0, 0.5, 1.2]}) == "overfitting"
