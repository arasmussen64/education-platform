import numpy as np

from checks import function, run


def test_the_output():
    """Prints the arrival point and the step count for both rates."""
    printed = run()
    assert printed == '[0. 0.] 72\n[0. 0.] 151\n', f"Your program printed:\n{printed}"


def test_the_rule():
    """On x² + y² from (3, 4) at rate 0.25 it arrives in a few dozen steps; with max_steps=5 it stops at 5."""
    descend = function("descend")
    p, steps = descend(lambda p: 2 * p, np.array([3.0, 4.0]), 0.25)
    assert np.linalg.norm(p) < 1e-6
    assert 10 < steps < 100
    p5, steps5 = descend(lambda p: 2 * p, np.array([3.0, 4.0]), 0.25, 1e-6, 5)
    assert steps5 == 5
    assert np.allclose(p5, [3.0 * 0.5**5, 4.0 * 0.5**5])
