from checks import function, run


def test_the_output():
    """Prints 1.6 then 1.08."""
    assert run() == '1.6\n1.08\n'


def test_the_velocity_is_returned():
    """From x = 1, v = 2, g = 3 at rate 0.1 and beta 0.9: v becomes 4.8 and x becomes 0.52."""
    momentum_step = function("momentum_step")
    x, v = momentum_step(1.0, 2.0, 3.0, 0.1, 0.9)
    assert abs(v - 4.8) < 1e-12
    assert abs(x - 0.52) < 1e-12
