import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints 1.964028 True."""
    assert run() == '1.964028 True\n'


def test_forward_keeps_every_value():
    """forward([x², x + 1], 3) is [3, 9, 10]."""
    forward = function("forward")
    assert forward([lambda x: x**2, lambda u: u + 1], 3.0) == [3.0, 9.0, 10.0]


def test_links_are_evaluated_at_their_own_inputs():
    """For x² then u³ at x = 2 the derivative is 192 (3u² at u = 4, times 2x); a chain of one exp at 0 gives 1."""
    chain_derivative = function("chain_derivative")
    d = chain_derivative([lambda x: x**2, lambda u: u**3], [lambda x: 2 * x, lambda u: 3 * u**2], 2.0)
    assert abs(d - 192.0) < 1e-9
    assert abs(chain_derivative([np.exp], [np.exp], 0.0) - 1.0) < 1e-12


def test_numeric_and_rule_agree_on_another_chain():
    """For x² then exp at 1.5, numeric and chain_derivative agree, and both are about 28.46."""
    chain_derivative = function("chain_derivative")
    numeric = function("numeric")
    functions = [lambda x: x**2, np.exp]
    d = chain_derivative(functions, [lambda x: 2 * x, np.exp], 1.5)
    assert abs(d - 3 * np.exp(2.25)) < 1e-9
    assert abs(numeric(functions, 1.5) - d) < 1e-5
