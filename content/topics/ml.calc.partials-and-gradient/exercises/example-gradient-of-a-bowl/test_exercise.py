from checks import run


def test_the_walkthrough():
    """Prints the gradient by rule and by check, the steepest direction and rate, two dot products, and two small walks."""
    assert run() == '[2. 6.]\n[2. 6.]\nTrue\n[0.316 0.949] 6.325\n6.325 0.0\n0.0635 0.0001\n'
