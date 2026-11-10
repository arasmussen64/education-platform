from checks import function, run


def test_the_output():
    """Prints the four names."""
    printed = run()
    assert printed == 'constant\nlinear\nquadratic\nfaster than quadratic\n', f"Your program printed:\n{printed}"


def test_the_borders():
    """A near-flat count is constant, an n log n count reads as linear, cubic growth is faster than quadratic."""
    growth_name = function("growth_name")
    assert growth_name([1000, 1000, 1001]) == "constant"
    assert growth_name([10000, 22000, 48000]) == "linear"
    assert growth_name([1, 8, 64]) == "faster than quadratic"
