import numpy as np

from checks import function, printed, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the thresholds, both reports, both intervals, the paired comparison and the verdict."""
    assert run() == 'thresholds 1.7 1.05\nA (39, 2, 22, 137) [0.88  0.951 0.639 0.765]\nB (35, 27, 26, 112) [0.735 0.565 0.574 0.569]\ninterval A [0.835 0.925]\ninterval B [0.674 0.796]\nA minus B 0.145 [0.075 0.215]\nverdict: A is better\n'


def test_confusion_and_metrics():
    """Hand-made labels give the four counts, and 8, 2, 4, 86 give accuracy 0.94, precision 0.8 and recall 2/3."""
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
    """Two identical models differ by exactly zero with a zero-width interval; a strictly better one has a positive interval."""
    paired_bootstrap = function("paired_bootstrap")
    rng = np.random.default_rng(0)
    correct = (rng.random(100) < 0.8).astype(int)
    assert paired_bootstrap(rng, correct, correct) == (0.0, 0.0, 0.0)
    better = correct.copy()
    better[correct == 0] = 1
    mean, low, high = paired_bootstrap(rng, better, correct)
    assert abs(mean - (1 - correct.mean())) < 1e-12 and 0 < low <= mean <= high


def test_choose_threshold():
    """On validation scores that separate perfectly at 1, the chosen threshold lies between the classes."""
    choose_threshold = function("choose_threshold")
    y_val = np.array([0, 0, 0, 1, 1, 1])
    score_val = np.array([0.1, 0.5, 0.9, 1.1, 1.5, 1.9])
    assert 0.9 <= choose_threshold(y_val, score_val) < 1.1


def test_the_verdict():
    """Two identical models get 'not established', and a model that is right wherever the other is wrong gets 'A is better'."""
    report = function("report")
    rng = np.random.default_rng(1)
    y = (rng.random(100) < 0.5).astype(int)
    scores = y * 1.0 + rng.normal(0, 1, size=100)
    same = printed(report, np.random.default_rng(2), y, scores, scores, 0.5, 0.5)
    assert same.strip().endswith("verdict: not established"), same
    perfect = y * 10.0
    better = printed(report, np.random.default_rng(3), y, perfect, scores, 5.0, 0.5)
    assert better.strip().endswith("verdict: A is better"), better
