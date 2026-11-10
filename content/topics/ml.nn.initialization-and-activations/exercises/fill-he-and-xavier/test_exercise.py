from checks import function, run


def test_the_output():
    """Prints the three scales."""
    printed = run()
    assert printed == '0.1 0.2 1.0\n', f"Your program printed:\n{printed}"


def test_more_widths():
    """Xavier for 784 inputs is about 0.0357 and He about 0.0505; He is always sqrt(2) times Xavier."""
    xavier_scale = function("xavier_scale")
    he_scale = function("he_scale")
    assert abs(xavier_scale(784) - 0.0357) < 1e-4 and abs(he_scale(784) - 0.0505) < 1e-4
    for n_in in (1, 16, 300):
        assert abs(he_scale(n_in) / xavier_scale(n_in) - 2 ** 0.5) < 1e-12
