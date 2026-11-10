from checks import function, run

EXPECTED = '1 1.9\n2 1.8002\n50 -0.0758\n'


def test_the_output():
    """Prints x after 1, 2 and 50 steps."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_first_step_from_elsewhere():
    """From -5 at rate 0.2 the first step lands at -4.8, and 200 steps at rate 0.05 end within 0.5 of zero."""
    adam = function("adam")
    assert abs(adam(-5.0, 0.2, 1) + 4.8) < 1e-9
    assert abs(adam(-5.0, 0.05, 200)) < 0.5
