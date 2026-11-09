from checks import function, printed, run


def test_program():
    """Running the program prints Hello, Ada! then Hi, Bob!"""
    got = run()
    assert got == "Hello, Ada!\nHi, Bob!\n", f"Your program printed:\n{got}"


def test_greet_order():
    """greet("Cy", "Yo") prints Yo, Cy!: the name first, then the greeting."""
    got = printed(function("greet"), "Cy", "Yo")
    assert got == "Yo, Cy!\n", f'greet("Cy", "Yo") printed:\n{got}'
