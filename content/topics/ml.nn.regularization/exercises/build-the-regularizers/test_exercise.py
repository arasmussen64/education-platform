import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == 'overfitting 0.478 2.115\nholding 0.386 drifting up 0.571\n28 48 0.478 48\n0.5 1.0\n'


def test_dropout_modes():
    """Training drops about p and scales survivors by 1 / (1 - p), backward uses the same mask, eval passes everything through, and Sequential flips the modes."""
    Dropout = function("Dropout")
    Sequential = function("Sequential")
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


def test_weight_decay_shrinks():
    """With a zero data gradient, Adam with decay pulls a weight towards zero; without decay it stays."""
    Adam = function("Adam")
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
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    Adam = function("Adam")
    make_blobs = function("make_blobs")
    evaluate = function("evaluate")
    fit = function("fit")
    X_train, y_train = make_blobs(20, seed=1, spread=1.8)
    X_val, y_val = make_blobs(100, seed=2, spread=1.8)
    net = Sequential([Dense(2, 64, seed=1, scale=1.0), ReLU(), Dense(64, 64, seed=2, scale=np.sqrt(2 / 64)), ReLU(), Dense(64, 3, seed=3)])
    loss = SoftmaxCrossEntropy()
    history = fit(net, loss, Adam(0.01), X_train, y_train, X_val, y_val, epochs=300, patience=10)
    assert history["stopped_at"] == history["best_epoch"] + 10 and len(history["val_loss"]) == history["stopped_at"]
    assert abs(evaluate(net, loss, X_val, y_val)[0] - min(history["val_loss"])) < 1e-9


def test_overfitting_and_a_cure():
    """The plain run's validation loss more than doubles from its low; with decay 0.03 it holds; the same seeds repeat exactly."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    Adam = function("Adam")
    make_blobs = function("make_blobs")
    fit = function("fit")
    read_fit = function("read_fit")
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
