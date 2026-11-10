import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def small_net():
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    return Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])


def data():
    make_blobs = function("make_blobs")
    split = function("split")
    X, y = make_blobs(100, seed=0)
    return split(X, y, seed=0)


def test_the_output():
    """Prints the five lines."""
    assert run() == '1.11 0.02 True\nlearning | stalled | diverging 240\n16 0\n[0.6, 0.8] 13.0\nTrue [1.0, 1.0]\n'


def test_norm_and_clip():
    """The norm is the length of everything together; clipping keeps the direction, lands on the limit, and leaves small gradients as they are."""
    gradient_norm = function("gradient_norm")
    clip_gradients = function("clip_gradients")
    rng = np.random.default_rng(2)
    grads = [rng.standard_normal((3, 4)), rng.standard_normal(5)]
    norm = gradient_norm(grads)
    assert isinstance(norm, float) and abs(norm - np.sqrt(sum((g ** 2).sum() for g in grads))) < 1e-12
    clipped = clip_gradients(grads, 0.5)
    assert abs(gradient_norm(clipped) - 0.5) < 1e-12 and np.allclose(clipped[0] / grads[0], clipped[1][0] / grads[1][0])
    assert clip_gradients(grads, norm + 1) is grads


def test_fit_records_and_clips():
    """One norm per step, recorded before clipping; entry 0 is the loss before training; a tiny limit keeps the weights almost where they started; the same seeds repeat exactly."""
    fit = function("fit")
    SGD = function("SGD")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    X_train, y_train, X_val, y_val = data()
    loss = SoftmaxCrossEntropy()
    plain = fit(small_net(), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=3)
    assert len(plain["grad_norms"]) == 24 and len(plain["train_loss"]) == len(plain["val_loss"]) == len(plain["val_accuracy"]) == 4
    assert abs(plain["train_loss"][0] - 1.10) < 0.02
    clipped = fit(small_net(), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=3, max_norm=0.01)
    assert abs(clipped["grad_norms"][0] - plain["grad_norms"][0]) < 1e-12 and plain["grad_norms"][0] > 0.01
    net = small_net()
    before = [p.copy() for p in net.parameters()]
    fit(net, loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=1, max_norm=1e-6)
    assert all(np.abs(p - b).max() < 1e-5 for p, b in zip(net.parameters(), before))
    again = fit(small_net(), loss, SGD(0.05), X_train, y_train, X_val, y_val, epochs=3)
    assert again["train_loss"] == plain["train_loss"] and again["grad_norms"] == plain["grad_norms"]


def test_diagnose():
    """Diverging, stalled, at chance and learning, from hand-made histories."""
    diagnose = function("diagnose")
    assert diagnose({"train_loss": [1.1, 0.5, float("nan")], "val_accuracy": [0.3, 0.3, 0.3]}, 3) == "diverging"
    assert diagnose({"train_loss": [1.1, 1.05, 1.0], "val_accuracy": [0.3, 0.3, 0.3]}, 3) == "stalled"
    assert diagnose({"train_loss": [1.1, 0.8, 0.5], "val_accuracy": [0.3, 0.3, 0.4]}, 3) == "at chance"
    assert diagnose({"train_loss": [1.1, 0.8, 0.5], "val_accuracy": [0.3, 0.6, 0.9]}, 3) == "learning"
    assert diagnose({"train_loss": [0.7, 0.3], "val_accuracy": [0.5, 0.58]}, 2) == "at chance"


def test_dead_and_overfit():
    """Three silenced units count as three; eight rows overfit to below a tenth and the network is left trained."""
    # One import for everything here, so the ReLU class dead_units looks for is the one the network was built with.
    dead_units = function("dead_units")
    overfit_one_batch, SoftmaxCrossEntropy, Dense, ReLU, Sequential, make_blobs, split = (dead_units.__globals__[name] for name in ("overfit_one_batch", "SoftmaxCrossEntropy", "Dense", "ReLU", "Sequential", "make_blobs", "split"))

    def net():
        return Sequential([Dense(2, 16, seed=1), ReLU(), Dense(16, 3, seed=2, scale=0.01)])

    X, y = make_blobs(100, seed=0)
    X_train, y_train, _, _ = split(X, y, seed=0)
    silenced = net()
    silenced.layers[0].b[:3] = -50.0
    assert dead_units(silenced, X_train) == 3 and dead_units(net(), X_train) == 0
    net = net()
    loss = SoftmaxCrossEntropy()
    first, last = overfit_one_batch(net, loss, X_train[:8], y_train[:8])
    assert abs(first - 1.11) < 0.02 and last < 0.1 and loss.forward(net.forward(X_train[:8]), y_train[:8]) < 0.1


def test_standardize():
    """Columns to mean 0 and spread 1 with the training set's numbers; the validation set gets the same numbers."""
    standardize = function("standardize")
    rng = np.random.default_rng(5)
    X_train = rng.normal(100.0, 20.0, size=(50, 2)) * np.array([1.0, 1000.0])
    X_val = rng.normal(100.0, 20.0, size=(10, 2)) * np.array([1.0, 1000.0])
    mean, std = X_train.mean(axis=0), X_train.std(axis=0)
    Z = standardize(X_train, mean, std)
    assert np.allclose(Z.mean(axis=0), 0.0) and np.allclose(Z.std(axis=0), 1.0)
    assert np.allclose(standardize(X_val, mean, std), (X_val - mean) / std)
