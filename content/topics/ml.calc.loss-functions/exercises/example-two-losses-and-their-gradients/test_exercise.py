from checks import run


def test_the_walkthrough():
    """Prints mean squared error and its gradient, cross-entropy, the sigmoid gradient and a softmax."""
    assert run() == '[-0.5  0.5  0.1 -0.2] 0.1375\n[-0.25  0.25  0.05 -0.1 ]\n[0.105 0.511 0.357 2.996] 0.992\n4.605 0.98\n[0.881 0.5   0.269]\n[-0.119  0.5   -0.731]\n[0.659 0.242 0.099] 1.0\n0.417\n'
