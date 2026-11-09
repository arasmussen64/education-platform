from checks import function, run


def test_report_lines():
    """report_lines gives one formatted line per student and then the Best line."""
    report_lines = function("report_lines")
    got = report_lines([{"name": "Dee", "scores": [100]}, {"name": "Eve", "scores": [65]}])
    assert got == ["Dee: 100.0 (A)", "Eve: 65.0 (D)", "Best: Dee"], f"report_lines returned {got!r}"


def test_program():
    """Running the program prints the tests' message and the report."""
    got = run()
    assert got == (
        "gradebook: all checks passed\nAda: 91.7 (A)\nBob: 72.3 (C)\nCy: 84.3 (B)\nBest: Ada\n"
    ), f"Your program printed:\n{got}"
