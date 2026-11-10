from checks import run


def test_the_walkthrough():
    """Prints the die's moments, a sample's, the running mean, two dice against one doubled, and five z-scores."""
    assert run() == '3.5 2.9167 1.708\n3.499 2.921\n10 3.0\n100 3.61\n1000 3.51\n10000 3.498\n100000 3.499\n6.999 5.858\n6.999 11.683\n[179.8 172.9 178.1 165.  152.9]\n[ 0.98  0.29  0.81 -0.5  -1.71]\n'
