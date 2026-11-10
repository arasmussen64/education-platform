from checks import run, run_with

EXPECTED = "117.0 dB\n"


def test_half_a_watt():
    """Prints 117.0 dB."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_any_power():
    """Works for any power: a millionth of a watt is 60.0 dB."""
    printed = run_with({"power": 1e-6})
    assert printed == "60.0 dB\n", (
        f"With power = 1e-6 it should print 60.0 dB. It printed:\n{printed}"
    )
