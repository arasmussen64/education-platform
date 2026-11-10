import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints True for power, exp, sigmoid and relu."""
    assert run() == 'power True\nexp True\nsigmoid True\nrelu True\n'


def test_numeric_derivative_is_central():
    """The estimate is within a millionth of 12 for x ** 3 at 2, and of exp(3) for exp at 3."""
    numeric_derivative = function("numeric_derivative")
    assert abs(numeric_derivative(lambda x: x**3, 2.0) - 12.0) < 1e-6
    assert abs(numeric_derivative(np.exp, 3.0) - np.exp(3.0)) < 1e-5


def test_sigmoid_pair():
    """d_sigmoid matches a central difference of sigmoid at four points, and keeps an array's shape."""
    sigmoid = function("sigmoid")
    d_sigmoid = function("d_sigmoid")
    for x in [-3.0, -1.0, 0.5, 2.0]:
        numeric = (sigmoid(x + 1e-6) - sigmoid(x - 1e-6)) / 2e-6
        assert abs(d_sigmoid(x) - numeric) < 1e-6
    assert d_sigmoid(np.array([[0.0, 1.0], [2.0, 3.0]])).shape == (2, 2)
    assert abs(float(d_sigmoid(0.0)) - 0.25) < 1e-9


def test_relu_pair():
    """relu keeps positives and zeroes negatives; d_relu is 1.0 on the right and 0.0 on the left."""
    relu = function("relu")
    d_relu = function("d_relu")
    assert relu(np.array([-1.0, 0.0, 2.5])).tolist() == [0.0, 0.0, 2.5]
    assert d_relu(np.array([-1.0, -0.1, 0.1, 2.0])).tolist() == [0.0, 0.0, 1.0, 1.0]
    assert str(d_relu(np.array([-1.0, 2.0]))) == "[0. 1.]"


def test_max_error_is_the_largest_gap():
    """With a rule that is wrong by exactly x, the max error over 0, 1, 2 is 2 (not the mean, 1)."""
    max_error = function("max_error")
    xs = np.array([0.0, 1.0, 2.0])
    assert max_error(lambda x: x**2, lambda x: 2 * x, xs) < 1e-6
    assert abs(max_error(lambda x: x**2, lambda x: 2 * x + x, xs) - 2.0) < 1e-5
