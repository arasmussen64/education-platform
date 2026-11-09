from checks import function, printed, run


def test_program():
    """Running the program prints hey three times."""
    printed_lines = run()
    assert printed_lines == "hey\nhey\nhey\n", f"Your program printed:\n{printed_lines}"


def test_other_arguments():
    """repeat("x", 2) prints x twice."""
    got = printed(function("repeat"), "x", 2)
    assert got == "x\nx\n", f'repeat("x", 2) printed:\n{got}'
