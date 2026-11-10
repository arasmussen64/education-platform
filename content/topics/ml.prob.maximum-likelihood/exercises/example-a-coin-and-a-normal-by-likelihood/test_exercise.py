from checks import run


def test_the_walkthrough():
    """Prints the coin's bias three ways, the normal's mean and spread, and the labels' likelihood against cross-entropy."""
    assert run() == '0.75 0.01112\n0.75 0.75\n0.75\n169.9 169.9\n9.89 9.89\n0.3024\n1.196 1.196\n'
