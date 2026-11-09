from checks import function, printed, run


def test_describe():
    """describe("Ada", 36) prints Ada is 36 years old."""
    got = printed(function("describe"), "Ada", 36)
    assert got == "Ada is 36 years old.\n", f'describe("Ada", 36) printed:\n{got}'


def test_describe_anyone():
    """describe("Cy", 50) prints Cy is 50 years old."""
    got = printed(function("describe"), "Cy", 50)
    assert got == "Cy is 50 years old.\n", f'describe("Cy", 50) printed:\n{got}'


def test_program():
    """Running the program describes Ada, then Bob."""
    got = run()
    assert got == "Ada is 36 years old.\nBob is 7 years old.\n", (
        f"Your program printed:\n{got}"
    )
