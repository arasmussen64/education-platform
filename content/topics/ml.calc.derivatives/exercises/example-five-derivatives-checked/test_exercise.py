from checks import run


def test_the_walkthrough():
    """Prints five checked derivatives, then the sigmoid's and ReLU's derivatives on an array."""
    assert run() == '12.0 12.0\n2.718282 2.718282\n0.25 0.25\n0.104994 0.104994\n0.0 1.0\n[0.0066 0.105  0.25   0.105  0.0066]\n[0. 0. 0. 1. 1.]\n'
