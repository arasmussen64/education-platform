from checks import function, run


def test_the_output():
    """Prints the four posteriors."""
    printed = run()
    assert printed == '0.088\n0.478\n0.905\n0.49\n', f"Your program printed:\n{printed}"


def test_edges():
    """Evidence that's equally likely either way leaves the prior alone; evidence impossible when false makes it certain."""
    posterior = function("posterior")
    assert abs(posterior(0.3, 0.5, 0.5) - 0.3) < 1e-12
    assert abs(posterior(0.3, 0.8, 0.0) - 1.0) < 1e-12
