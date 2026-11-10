import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints both reports, the interval and the paired comparison."""
    assert run() == 'A (61, 21, 13, 105) [0.83  0.744 0.824 0.782]\nB (53, 31, 21, 95) [0.74  0.631 0.716 0.671]\ninterval for A [0.778 0.882]\nA minus B [0.09  0.015 0.165]\n'


def test_confusion_and_metrics():
    """Hand-made labels give the four counts, and 8, 2, 4, 86 give accuracy 0.94, precision 0.8, recall 2/3."""
    confusion = function("confusion")
    metrics = function("metrics")
    y = np.array([1, 1, 0, 0, 1, 0])
    pred = np.array([1, 0, 1, 0, 1, 0])
    assert confusion(y, pred) == (2, 1, 1, 2)
    accuracy, precision, recall, f1 = metrics(8, 2, 4, 86)
    assert abs(accuracy - 0.94) < 1e-12 and abs(precision - 0.8) < 1e-12 and abs(recall - 2 / 3) < 1e-12


def test_accuracy_interval():
    """An accuracy of 0.9 on 100 examples has the interval 0.841 to 0.959."""
    accuracy_interval = function("accuracy_interval")
    low, high = accuracy_interval(np.array([1] * 90 + [0] * 10))
    assert abs(low - 0.8412) < 0.001 and abs(high - 0.9588) < 0.001


def test_paired_bootstrap():
    """Two identical models differ by exactly zero with a zero-width interval; a model that is right where the other is wrong on a fifth of examples differs by 0.2."""
    paired_bootstrap = function("paired_bootstrap")
    rng = np.random.default_rng(0)
    correct = (rng.random(100) < 0.8).astype(int)
    assert paired_bootstrap(rng, correct, correct) == (0.0, 0.0, 0.0)
    better = correct.copy()
    better[correct == 0] = 1
    mean, low, high = paired_bootstrap(rng, better, correct)
    assert abs(mean - (1 - correct.mean())) < 1e-12 and 0 < low <= mean <= high
