from checks import run


def test_the_walkthrough():
    """Prints the arrays, shapes, slices, sums and ranges shown in the steps."""
    assert run() == (
        "[1.5 2.  3.5]\n(3,) float64\n(2, 3)\n6\n[1 4]\n[3. 4. 7.]\n"
        "[[11 22 33]\n [14 25 36]]\n[5 7 9]\n[2. 5.]\n"
        "[0 1 2 3 4]\n[0.   0.25 0.5  0.75 1.  ]\n"
    )
