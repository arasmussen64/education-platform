from checks import run


def test_the_walkthrough():
    """Prints the solution, the check, the eliminated rows, the hand solution and two ranks."""
    assert run() == (
        "[2. 1.]\n[5. 1.]\nTrue\n[[ 2.   1.   5. ]\n [ 0.  -1.5 -1.5]]\n2.0 1.0\n2\n1\n"
    )
