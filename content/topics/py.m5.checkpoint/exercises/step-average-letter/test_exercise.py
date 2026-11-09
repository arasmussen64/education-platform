from checks import function, run


def test_average_and_grades():
    """average([90, 80]) is 85.0; 90 is an A, 89.9 and 80 are a B."""
    average = function("average")
    letter_grade = function("letter_grade")
    assert average([90, 80]) == 85.0, f"average([90, 80]) returned {average([90, 80])!r}"
    assert letter_grade(90) == "A", f"letter_grade(90) returned {letter_grade(90)!r}"
    assert letter_grade(89.9) == "B", f"letter_grade(89.9) returned {letter_grade(89.9)!r}"
    assert letter_grade(80) == "B", f"letter_grade(80) returned {letter_grade(80)!r}"


def test_program():
    """Running the program prints the tests' message and the report."""
    got = run()
    assert got == (
        "gradebook: all checks passed\nAda: 91.7 (A)\nBob: 72.3 (C)\nCy: 84.3 (B)\nBest: Ada\n"
    ), f"Your program printed:\n{got}"
