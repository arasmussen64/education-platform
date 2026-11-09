from checks import function, run


def test_program():
    """Running the program prints the tests' message and the report."""
    got = run()
    assert got == (
        "gradebook: all checks passed\nAda: 91.7 (A)\nBob: 72.3 (C)\nCy: 84.3 (B)\nBest: Ada\n"
    ), f"Your program printed:\n{got}"


def test_functions():
    """The pieces work on other data too: a grade boundary, a tie, and a one-student report."""
    assert function("letter_grade")(80) == "B", "letter_grade(80) should be B"
    tie = [{"name": "X", "scores": [80]}, {"name": "Y", "scores": [80]}]
    assert function("best_student")(tie) == "X", "best_student should pick the first of a tie"
    got = function("report_lines")([{"name": "Dee", "scores": [100]}])
    assert got == ["Dee: 100.0 (A)", "Best: Dee"], f"report_lines returned {got!r}"


def test_docstrings():
    """Every function has a docstring."""
    for name in ("average", "letter_grade", "best_student", "report_lines", "main"):
        assert (function(name).__doc__ or "").strip() != "", f"{name} needs a docstring"
