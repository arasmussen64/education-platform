from checks import function, run


def test_the_output():
    """Prints the three gaps two ways and the two directions."""
    printed = run()
    assert printed == '0.0 0.0\n0.123 0.123\n0.428 0.428\n0.531 0.737\n', f"Your program printed:\n{printed}"


def test_properties():
    """KL is 0 for equal distributions, positive otherwise, and 1 bit from a certainty to a fair coin."""
    kl = function("kl")
    assert kl([0.3, 0.7], [0.3, 0.7]) == 0
    assert kl([0.3, 0.7], [0.5, 0.5]) > 0
    assert abs(kl([1.0, 0.0], [0.5, 0.5]) - 1.0) < 1e-12
