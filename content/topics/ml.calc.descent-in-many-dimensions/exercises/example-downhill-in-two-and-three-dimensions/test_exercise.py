from checks import run


def test_the_walkthrough():
    """Prints the path down the bowl, four rates compared, the plane fit's loss curve, the plane and the lstsq check."""
    assert run() == '0 [4. 2.] 28.0\n1 [3.2 0.8] 12.16\n2 [2.56 0.32] 6.8608\n5 [1.311 0.02 ] 1.7192\n10 [0.429 0.   ] 0.1845\n0.05 1.955\n0.1 0.184\n0.3 0.138\n0.4 10040.191\n21.2408 0.7298 0.0063 0.0063\n[ 2.015 -1.035  3.024]\nTrue\n'
