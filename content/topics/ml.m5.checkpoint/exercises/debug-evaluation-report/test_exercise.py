import numpy as np

from checks import function, run

EXPECTED = 'thresholds 1.7 1.05\nA (39, 2, 22, 137) [0.88  0.951 0.639 0.765]\nB (35, 27, 26, 112) [0.735 0.565 0.574 0.569]\ninterval A [0.835 0.925]\ninterval B [0.674 0.796]\nA minus B 0.145 [0.075 0.215]\nverdict: A is better\n'


def test_the_output():
    """Prints the thresholds, both reports, both intervals, the paired comparison and the verdict."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_thresholds_come_from_validation():
    """The first line reads 'thresholds 1.7 1.05', and perfectly separated scores put the threshold between the classes."""
    assert run().startswith("thresholds 1.7 1.05\n")
    choose_threshold = function("choose_threshold")
    assert 0.8 <= choose_threshold(np.array([0, 0, 1, 1]), np.array([0.2, 0.8, 1.2, 1.8])) < 1.2


def test_metrics_and_pairing():
    """8, 2, 4, 86 give precision 0.8 and recall 2/3, and two identical models differ by exactly zero."""
    metrics = function("metrics")
    paired_bootstrap = function("paired_bootstrap")
    assert abs(metrics(8, 2, 4, 86)[1] - 0.8) < 1e-12 and abs(metrics(8, 2, 4, 86)[2] - 2 / 3) < 1e-12
    correct = np.array([1, 0, 1, 1, 0, 1, 1, 1])
    assert paired_bootstrap(np.random.default_rng(0), correct, correct) == (0.0, 0.0, 0.0)
