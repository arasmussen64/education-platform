from checks import run


def test_the_walkthrough():
    """Prints the stretched, rotated and sheared vectors, both compositions, the identity's work, the inverse and three determinants."""
    assert run() == (
        "[2. 1.]\n[2. 0.] [0. 1.]\n[0. 1.]\n[-1.  0.]\n[1. 1.]\n[-1.  2.] [0. 1.]\n"
        "[1. 1.]\n[[0.5 0. ]\n [0.  1. ]]\n[1. 1.]\n2\n1\n1\n"
    )
