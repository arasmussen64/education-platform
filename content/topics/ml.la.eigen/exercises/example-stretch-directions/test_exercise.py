from checks import run


def test_the_walkthrough():
    """Prints the eigenvalues, a checked pair, a turned vector, five applications, and complex eigenvalues."""
    assert run() == (
        "[1. 3.]\n[2.121 2.121] [2.121 2.121]\n[2. 1.]\n[122. 121.]\n[0.71  0.704]\n[0.-1.j 0.+1.j]\n"
    )
