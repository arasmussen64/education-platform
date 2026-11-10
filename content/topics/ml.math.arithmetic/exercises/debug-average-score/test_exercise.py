from checks import run, run_with

EXPECTED = "Average: 19.0 out of 30\nPercent: 63.3%\n"


def test_these_quizzes():
    """Prints Average: 19.0 out of 30, then Percent: 63.3%."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )


def test_any_quizzes():
    """Works for any marks: 10, 20 and 30 out of 40 give 20.0 and 50.0%."""
    printed = run_with({"quiz1": 10, "quiz2": 20, "quiz3": 30, "out_of": 40})
    assert printed == "Average: 20.0 out of 40\nPercent: 50.0%\n", (
        f"With marks 10, 20 and 30 out of 40 it should print Average: 20.0 out of 40, then Percent: 50.0%. It printed:\n{printed}"
    )
