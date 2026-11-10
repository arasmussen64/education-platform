import numpy as np

from checks import function, run

EXPECTED = 'gradient shapes match the parameters: True | worst gap: under 1e-6\n'


def test_the_output():
    """Prints matching shapes and a worst gap under a millionth."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_on_other_data():
    """The check passes on random data through a deeper stack, and a ReLU passes a gradient only where its input was positive."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    MSELoss = function("MSELoss")
    gradient_check = function("gradient_check")
    X = np.random.default_rng(8).standard_normal((5, 3))
    y = np.random.default_rng(9).standard_normal((5, 2))
    assert gradient_check(Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 4, seed=2), ReLU(), Dense(4, 2, seed=3)]), MSELoss(), X, y) < 1e-6
    relu = ReLU()
    relu.forward(np.array([[1.0, -1.0]]))
    assert relu.backward(np.array([[-3.0, 3.0]])).tolist() == [[-3.0, 0.0]]
