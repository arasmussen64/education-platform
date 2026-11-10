import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the seven lines."""
    assert run() == '0.1 0.1414213562373095 0.2\n0.01 tanh vanished vanished\nXavier tanh stable stable\n0.1 ReLU drifting drifting\nHe ReLU stable stable\n0.96 0.68\nTrue True False\n'


def test_scales():
    """Xavier and He match their formulas for several widths."""
    xavier_scale = function("xavier_scale")
    he_scale = function("he_scale")
    for n_in in (2, 50, 784):
        assert abs(xavier_scale(n_in) - (1 / n_in) ** 0.5) < 1e-12 and abs(he_scale(n_in) - (2 / n_in) ** 0.5) < 1e-12


def test_sizes_through_depth():
    """A six-layer ReLU stack under He keeps activations and the input gradient between 0.1 and 10; under 0.01 both fall below 1e-3."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    activation_stds = function("activation_stds")
    input_gradient_std = function("input_gradient_std")
    he_scale = function("he_scale")
    X = np.random.default_rng(1).standard_normal((128, 64))
    good = Sequential([piece for i in range(6) for piece in (Dense(64, 64, seed=i, scale=he_scale(64)), ReLU())])
    stds = activation_stds(good, X)
    assert len(stds) == 12 and 0.1 <= stds[-1] <= 10 and 0.1 <= input_gradient_std(good, X) <= 10
    bad = Sequential([piece for i in range(6) for piece in (Dense(64, 64, seed=i, scale=0.01), ReLU())])
    assert activation_stds(bad, X)[-1] < 1e-3 and input_gradient_std(bad, X) < 1e-3


def test_counts():
    """Dead units are columns that never fire; saturation counts both signs; identical columns are not the same as a constant matrix."""
    dead_fraction = function("dead_fraction")
    saturated_fraction = function("saturated_fraction")
    units_identical = function("units_identical")
    assert dead_fraction(np.array([[0.0, 0.0, 1.0], [0.0, 2.0, 0.0]])) == 1 / 3
    assert saturated_fraction(np.array([[-5.0, 5.0, 3.0, -3.0]])) == 0.5 and saturated_fraction(np.array([[-5.0, 5.0, 3.0, -3.0]]), threshold=2.5) == 1.0
    assert units_identical(np.tile(np.array([[0.3], [-0.7], [0.1]]), (1, 6))) and not units_identical(np.array([[1.0, 2.0], [1.0, 2.0]]))
    assert units_identical(np.full((3, 3), 0.5))
