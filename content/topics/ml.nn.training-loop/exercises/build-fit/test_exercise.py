import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three lines."""
    assert run() == '240 60 [30, 30, 30]\n0.446 0.151 0.92 converging\n[4, 4, 2] 0.6666666666666666\n'


def test_batches_and_split():
    """Batches cover every index once and reshuffle between epochs; the split is disjoint, complete and seeded."""
    batches = function("batches")
    split = function("split")
    make_blobs = function("make_blobs")
    rng = np.random.default_rng(2)
    one, two = list(batches(23, 5, rng)), list(batches(23, 5, rng))
    assert [len(index) for index in one] == [5, 5, 5, 5, 3] and sorted(np.concatenate(one).tolist()) == list(range(23))
    assert not np.array_equal(np.concatenate(one), np.concatenate(two))
    X, y = make_blobs(50, seed=3)
    assert X.shape == (150, 2) and np.bincount(y).tolist() == [50, 50, 50]
    X_train, y_train, X_val, y_val = split(X, y, seed=4)
    assert len(X_train) == 120 and len(X_val) == 30
    rows = {tuple(row) for row in X_train} | {tuple(row) for row in X_val}
    assert len(rows) == 150 and not ({tuple(row) for row in X_train} & {tuple(row) for row in X_val})
    again = split(X, y, seed=4)
    assert np.array_equal(again[0], X_train) and not np.array_equal(split(X, y, seed=5)[0], X_train)


def test_evaluate_does_not_train():
    """evaluate returns the loss and the accuracy and leaves every weight exactly as it was."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    evaluate = function("evaluate")
    make_blobs = function("make_blobs")
    X, y = make_blobs(20, seed=1)
    net = Sequential([Dense(2, 8, seed=1), ReLU(), Dense(8, 3, seed=2)])
    before = [p.copy() for p in net.parameters()]
    value, acc = evaluate(net, SoftmaxCrossEntropy(), X, y)
    assert 0 <= acc <= 1 and value > 0
    assert all(np.array_equal(a, b) for a, b in zip(before, net.parameters()))


def test_fit_learns_and_repeats():
    """fit reaches 85 percent validation accuracy within 30 epochs, repeats exactly with the same seed, and differs with another."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    SGD = function("SGD")
    fit = function("fit")
    make_blobs = function("make_blobs")
    split = function("split")
    X, y = make_blobs(80, seed=7)
    X_train, y_train, X_val, y_val = split(X, y, seed=7)

    def run_once(seed):
        net = Sequential([Dense(2, 16, seed=3, scale=1.0), ReLU(), Dense(16, 3, seed=4)])
        return fit(net, SoftmaxCrossEntropy(), SGD(0.05), X_train, y_train, X_val, y_val, epochs=30, batch_size=16, seed=seed)

    first = run_once(1)
    assert len(first["train_loss"]) == 30 and first["val_accuracy"][-1] >= 0.85
    assert first["train_loss"][-1] < first["train_loss"][0]
    assert run_once(1)["train_loss"] == first["train_loss"]
    assert run_once(2)["train_loss"] != first["train_loss"]


def test_read_curve():
    """A falling curve converges, a flat one stalls, a rising or NaN one diverges."""
    read_curve = function("read_curve")
    assert read_curve([1.1, 0.8, 0.5, 0.3]) == "converging"
    assert read_curve([1.10, 1.09, 1.09, 1.08]) == "stalled"
    assert read_curve([1.1, 1.3, 2.0, 7.4]) == "diverging" and read_curve([1.1, 2.0, float("nan")]) == "diverging"
