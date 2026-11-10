from checks import run


def test_the_walkthrough():
    """Prints the population, three standard errors, a histogram of means, an interval, its coverage and a bootstrap interval."""
    assert run() == '10.01 9.95 6.95\n2 9.95 7.01 7.07\n10 10.01 3.15 3.16\n50 10.01 1.41 1.41\n  5.0 \n  6.0 #\n  7.0 ######\n  8.0 #################\n  9.0 ###########################\n 10.0 #########################\n 11.0 ###############\n 12.0 ######\n 13.0 ##\n 14.0 \n10.8 1.58 7.7 13.9\n0.9385\n7.71 [ 3.55 11.36]\n'
