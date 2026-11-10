from checks import run


def test_the_walkthrough():
    """Prints ten flips, a binomial table against its formula, a uniform check and the 68-95-99.7 rule."""
    assert run() == '[0 0 1 0 0 0 0 0 0 1] 2\n[ 2802 12129 23513 26456 19994]\n0 0.028 0.028 #\n1 0.121 0.121 ######\n2 0.235 0.233 ############\n3 0.265 0.267 #############\n4 0.2 0.2 ##########\n0.249 0.0\n170.0 10.0\n1 0.684\n2 0.955\n3 0.997\n'
