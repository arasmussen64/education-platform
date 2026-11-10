import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints [0. 3.], [0. 2.] and None."""
    assert run() == "[0. 3.]\n[0. 2.]\nNone\n"


def test_compose_applies_in_order():
    """compose(A, B, C) @ v is C @ (B @ (A @ v)), and compose(A) is A."""
    compose = function("compose")
    A = np.array([[1.0, 2.0], [0.0, 1.0]])
    B = np.array([[0.0, -1.0], [1.0, 0.0]])
    C = np.array([[3.0, 0.0], [0.0, 0.5]])
    v = np.array([1.0, -2.0])
    assert np.allclose(compose(A, B, C) @ v, C @ (B @ (A @ v)))
    assert np.allclose(compose(A), A)


def test_undo():
    """undo(M) @ M is the identity when M has an inverse, and undo is None when it hasn't."""
    undo = function("undo")
    M = np.array([[2.0, 1.0], [1.0, 3.0]])
    assert np.allclose(undo(M) @ M, np.eye(2))
    assert undo(np.array([[1.0, 1.0], [1.0, 1.0]])) is None
    assert undo(np.array([[0.0, 0.0], [0.0, 0.0]])) is None
