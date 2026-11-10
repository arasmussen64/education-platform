import numpy as np

from checks import function, run

EXPECTED = 'coin 0.75\nnormal 169.9\n'


def test_the_output():
    """Prints the coin's bias and the normal's mean."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_two_functions():
    """The coin's likelihood of 2 heads in 3 peaks at 2/3, and the normal's log-likelihood is highest at the sample mean."""
    coin_likelihood = function("coin_likelihood")
    normal_log_likelihood = function("normal_log_likelihood")
    ps = np.linspace(0.01, 0.99, 99)
    assert abs(ps[coin_likelihood(ps, 2, 3).argmax()] - 0.67) < 0.011
    x = np.array([1.0, 2.0, 3.0, 6.0])
    mus = np.array([2.0, 3.0, 4.0])
    assert normal_log_likelihood(mus, x, 1.0).argmax() == 1
