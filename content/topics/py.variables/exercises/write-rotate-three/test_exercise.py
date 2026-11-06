from checks import run, run_with


def test_prints_rotated():
    """Prints the values rotated: 2 3 1."""
    printed = run()
    assert printed == "2 3 1\n", f"Expected 2 3 1. Your program printed:\n{printed}"


def test_rotates_any_values():
    """Rotates any three values, not just 1, 2 and 3."""
    printed = run_with({"a": "x", "b": "y", "c": "z"})
    assert printed == "y z x\n", (
        "Starting with a, b and c as x, y and z, it should print y z x. "
        f"It printed:\n{printed}\nMove the values using the names."
    )
