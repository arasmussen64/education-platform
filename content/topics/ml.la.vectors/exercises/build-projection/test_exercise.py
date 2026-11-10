import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four vectors."""
    assert run() == "[3. 0.]\n[0. 4.]\n[3.5 3.5]\n[-0.5  0.5]\n"


def test_three_dimensions():
    """Projecting [1, 2, 3] onto [0, 0, 2] gives [0, 0, 3]; the rejection is [1, 2, 0]."""
    project = function("project")
    rejection = function("rejection")
    v = np.array([1.0, 2.0, 3.0])
    onto = np.array([0.0, 0.0, 2.0])
    assert project(v, onto).tolist() == [0.0, 0.0, 3.0]
    assert rejection(v, onto).tolist() == [1.0, 2.0, 0.0]


def test_the_geometry():
    """For another pair: the projection lies along onto, the rejection is perpendicular to it, and they add up to v."""
    project = function("project")
    rejection = function("rejection")
    v = np.array([2.0, -1.0, 4.0])
    onto = np.array([3.0, 1.0, -2.0])
    p = project(v, onto)
    r = rejection(v, onto)
    assert np.allclose(p, (p @ onto) / (onto @ onto) * onto)
    assert abs(r @ onto) < 1e-9
    assert np.allclose(p + r, v)
