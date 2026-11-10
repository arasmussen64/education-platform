import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the populations after one and ten years, then the steady state."""
    assert run() == "[900. 100.]\n[676.1 323.9]\n[0.667 0.333]\n"


def test_after_years():
    """after_years agrees with applying T repeatedly."""
    after_years = function("after_years")
    T = np.array([[0.7, 0.4], [0.3, 0.6]])
    start = np.array([10.0, 20.0])
    by_hand = start.copy()
    for _ in range(7):
        by_hand = T @ by_hand
    assert np.allclose(after_years(T, start, 7), by_hand)


def test_steady_state():
    """The steady state is kept by T, sums to 1, and is right for a 2-by-2 and a 3-by-3."""
    steady_state = function("steady_state")
    T = np.array([[0.7, 0.4], [0.3, 0.6]])
    s = steady_state(T)
    assert np.allclose(T @ s, s)
    assert abs(s.sum() - 1) < 1e-9
    assert np.allclose(s, [4 / 7, 3 / 7])
    T3 = np.array([[0.5, 0.3, 0.2], [0.3, 0.4, 0.3], [0.2, 0.3, 0.5]])
    s3 = steady_state(T3)
    assert np.allclose(T3 @ s3, s3)
    assert abs(s3.sum() - 1) < 1e-9
