from checks import function, run


def test_the_output():
    """Prints 0.088 and 0.632."""
    assert run() == '0.088\n0.632\n'


def test_other_values():
    """Evidence equally likely either way leaves the prior; a prior of 0.5 with likelihoods 0.9 and 0.1 gives 0.9."""
    bayes = function("bayes")
    assert abs(bayes(0.2, 0.4, 0.4) - 0.2) < 1e-12
    assert abs(bayes(0.5, 0.9, 0.1) - 0.9) < 1e-12
