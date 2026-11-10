from checks import run


def test_the_walkthrough():
    """Prints the design matrix, the exact fit twice, the fitted values, the noisy fit and two zeros."""
    assert run() == (
        "[[1. 1.]\n [2. 1.]\n [3. 1.]\n [4. 1.]\n [5. 1.]]\n[2. 1.]\n[2. 1.]\n"
        "[ 3.  5.  7.  9. 11.]\n[1.95 1.15]\n0.0 0.0\n"
    )
