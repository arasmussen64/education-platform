from checks import function, run


def test_the_output():
    """Prints the eleven rows and the total 1.0."""
    printed = run()
    assert printed == '0 0.028 #\n1 0.121 ######\n2 0.233 ############\n3 0.267 #############\n4 0.2 ##########\n5 0.103 #####\n6 0.037 ##\n7 0.009 \n8 0.001 \n9 0.0 \n10 0.0 \n1.0\n', f"Your program printed:\n{printed}"


def test_known_values():
    """Three fair flips: no heads 0.125, one head 0.375; a certain try gives 1 for k = n and 0 otherwise."""
    binomial_pmf = function("binomial_pmf")
    assert abs(binomial_pmf(0, 3, 0.5) - 0.125) < 1e-12
    assert abs(binomial_pmf(1, 3, 0.5) - 0.375) < 1e-12
    assert binomial_pmf(5, 5, 1.0) == 1 and binomial_pmf(4, 5, 1.0) == 0
