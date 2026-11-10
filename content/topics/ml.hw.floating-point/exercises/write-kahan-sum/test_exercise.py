from checks import function, run


def test_the_output():
    """Prints the plain and the Kahan totals."""
    printed = run()
    assert printed == 'plain: 9998.556640625\nkahan: 10000.0\n', f"Your program printed:\n{printed}"


def test_within_a_thousandth():
    """A hundred thousand tenths come to 10,000 within 0.001, and a thousand values of 0.001 to 1 within 1e-6."""
    kahan_sum = function("kahan_sum")
    assert abs(kahan_sum([0.1] * 100_000) - 10000) < 0.001
    assert abs(kahan_sum([0.001] * 1000) - 1.0) < 1e-6
