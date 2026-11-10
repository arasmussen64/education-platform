import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three intervals."""
    printed = run()
    assert printed == '(0.845, 0.795, 0.895)\n(0.845, 0.82, 0.87)\n(1.0, 1.0, 1.0)\n', f"Your program printed:\n{printed}"


def test_a_known_case():
    """An accuracy of 0.9 on 100 examples has a standard error of 0.03 and an interval of 0.841 to 0.959."""
    accuracy_interval = function("accuracy_interval")
    correct = np.array([1] * 90 + [0] * 10)
    assert accuracy_interval(correct) == (0.9, 0.841, 0.959)
