import numpy as np

from checks import function, run


def test_the_output():
    """Prints True for all four rules."""
    printed = run()
    assert printed == 'x**2 True\nexp True\nlog True\nsigmoid True\n', f"Your program printed:\n{printed}"


def test_accuracy():
    """The estimate is within a millionth of the exact derivative for x ** 3 at 2 and exp at 3."""
    derivative = function("derivative")
    assert abs(derivative(lambda x: x**3, 2.0) - 12.0) < 1e-6
    assert abs(derivative(np.exp, 3.0) - np.exp(3.0)) < 1e-5
