from checks import function, run


def test_program():
    """Run directly, the file prints that all checks passed."""
    got = run()
    assert got == "to_fahrenheit: all checks passed\n", f"Your program printed:\n{got}"


def test_catches_a_bug():
    """With a broken to_fahrenheit (celsius * 2 + 32), test_to_fahrenheit fails."""
    test = function("test_to_fahrenheit")
    import solution

    original = solution.to_fahrenheit
    solution.to_fahrenheit = lambda celsius: celsius * 2 + 32
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.to_fahrenheit = original
    assert caught, (
        "test_to_fahrenheit passed even with a wrong formula: "
        "each assert must compare with the real expected value"
    )
