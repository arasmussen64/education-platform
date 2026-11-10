import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the standardized grid, rounded."""
    assert run() == "[[-1.22 -1.22]\n [ 0.    0.  ]\n [ 1.22  1.22]]\n"


def test_columns_end_with_mean_0_and_std_1():
    """Every column of a 4-by-3 grid ends with mean 0 and standard deviation 1, and the shape is kept."""
    standardize = function("standardize")
    grid = np.array([[2.0, 100.0, -1.0], [4.0, 150.0, 0.0], [6.0, 50.0, 3.0], [8.0, 200.0, 2.0]])
    result = standardize(grid)
    assert result.shape == (4, 3)
    assert np.allclose(result.mean(axis=0), 0)
    assert np.allclose(result.std(axis=0), 1)


def test_one_column():
    """A single column works, and the original grid is left unchanged."""
    standardize = function("standardize")
    grid = np.array([[1.0], [3.0], [5.0]])
    result = standardize(grid)
    assert np.allclose(result[:, 0], [-1.2247, 0.0, 1.2247], atol=1e-3)
    assert grid.tolist() == [[1.0], [3.0], [5.0]]
