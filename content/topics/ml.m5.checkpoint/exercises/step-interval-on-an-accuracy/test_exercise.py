import numpy as np

from checks import function, run


def test_the_output():
    """Prints both accuracies with their intervals."""
    printed = run()
    assert printed == '0.885 [0.841 0.929]\n0.705 [0.642 0.768]\n', f"Your program printed:\n{printed}"


def test_a_known_accuracy():
    """0.9 on 100 examples spans 0.841 to 0.959."""
    accuracy_interval = function("accuracy_interval")
    low, high = accuracy_interval(np.array([1] * 90 + [0] * 10))
    assert abs(low - 0.8412) < 0.001 and abs(high - 0.9588) < 0.001
