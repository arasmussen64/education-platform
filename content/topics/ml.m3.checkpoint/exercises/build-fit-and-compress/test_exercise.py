import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXACT = np.array([[0.0, 0.0, 3.0], [1.0, 0.0, 5.0], [0.0, 1.0, 2.0], [2.0, 3.0, 4.0], [3.0, 1.0, 8.0], [1.0, 2.0, 3.0]])


def test_the_output():
    """Prints the plane, the lstsq check, the variance kept and the compression error."""
    assert run() == 'plane [ 2.015 -1.035  3.024]\nlstsq agrees True\nvariance kept 0.9998\ncompression error 0.079\n'


def test_fit_matches_lstsq():
    """fit_plane agrees with np.linalg.lstsq on other points, and finds an exact plane exactly."""
    fit_plane = function("fit_plane")
    other = np.array([[1.0, 1.0, 2.0], [2.0, 0.0, 7.0], [0.0, 3.0, -1.0], [4.0, 2.0, 9.5], [3.0, 3.0, 5.0]])
    A = np.column_stack([other[:, 0], other[:, 1], np.ones(5)])
    assert np.allclose(fit_plane(other), np.linalg.lstsq(A, other[:, 2])[0])
    assert np.allclose(fit_plane(EXACT), [2.0, -1.0, 3.0])


def test_compress():
    """compress returns shares that sum to 1 in descending order; three components rebuild exactly, two leave an error of sqrt((n - 1) times the smallest eigenvalue)."""
    compress = function("compress")
    other = np.array([[1.0, 1.0, 2.0], [2.0, 0.0, 7.0], [0.0, 3.0, -1.0], [4.0, 2.0, 9.5], [3.0, 3.0, 5.0]])
    shares, rebuilt = compress(other, 3)
    assert abs(shares.sum() - 1) < 1e-9
    assert (np.diff(shares) <= 1e-12).all()
    assert np.allclose(rebuilt, other)
    shares2, rebuilt2 = compress(other, 2)
    values = np.linalg.eigvalsh(np.cov(other, rowvar=False))
    assert abs(np.linalg.norm(other - rebuilt2) ** 2 - 4 * values[0]) < 1e-9


def test_exact_plane():
    """Points exactly on a plane: two components keep all the variance and rebuild them exactly."""
    compress = function("compress")
    shares, rebuilt = compress(EXACT, 2)
    assert abs(shares[:2].sum() - 1) < 1e-9
    assert np.allclose(rebuilt, EXACT)
