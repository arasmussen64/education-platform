from checks import function, run


def test_best_student():
    """best_student returns Ada here, and the first of two who tie."""
    best_student = function("best_student")
    students = [
        {"name": "Ada", "scores": [95, 88, 92]},
        {"name": "Bob", "scores": [72, 65, 80]},
    ]
    assert best_student(students) == "Ada", f"best_student returned {best_student(students)!r}"
    tie = [{"name": "X", "scores": [80]}, {"name": "Y", "scores": [80]}]
    assert best_student(tie) == "X", f"with a tie, best_student returned {best_student(tie)!r}"


def test_program():
    """Running the program prints the tests' message and the report."""
    got = run()
    assert got == (
        "gradebook: all checks passed\nAda: 91.7 (A)\nBob: 72.3 (C)\nCy: 84.3 (B)\nBest: Ada\n"
    ), f"Your program printed:\n{got}"
