from checks import function, run


def test_the_output():
    """Prints the two losses and the three fitted biases."""
    printed = run()
    assert printed == '4.4987 5.5452\n0.75 0.3 0.5\n', f"Your program printed:\n{printed}"


def test_the_loss_is_lowest_at_the_fraction():
    """For 2 heads in 5 the loss is lower at 0.4 than at 0.3 or 0.5, and fit_coin lands within 0.001 of 0.4."""
    nll = function("negative_log_likelihood")
    fit_coin = function("fit_coin")
    assert nll(0.4, 2, 5) < nll(0.3, 2, 5) and nll(0.4, 2, 5) < nll(0.5, 2, 5)
    assert abs(fit_coin(2, 5) - 0.4) < 0.001
