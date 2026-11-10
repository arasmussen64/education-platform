from checks import function, run


def test_the_output():
    """Prints the three intensities."""
    printed = run()
    assert printed == '170.7\n0.5 28.4\n', f"Your program printed:\n{printed}"


def test_more_shapes():
    """A (2, 3) @ (3, 4) in float64 is 48 FLOPs over 208 bytes, and float16 doubles the intensity of a 256-cube."""
    arithmetic_intensity = function("arithmetic_intensity")
    assert abs(arithmetic_intensity(2, 3, 4, 8) - 48 / 208) < 1e-12
    assert abs(arithmetic_intensity(256, 256, 256, 2) - 2 * arithmetic_intensity(256, 256, 256, 4)) < 1e-9
