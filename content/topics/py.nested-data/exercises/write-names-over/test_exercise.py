from checks import function

STUDENTS = [
    {"name": "Ada", "score": 91},
    {"name": "Bob", "score": 78},
    {"name": "Cy", "score": 80},
]


def test_over_eighty():
    """With a limit of 80, only Ada is over: 80 itself doesn't count."""
    names_over = function("names_over")
    got = names_over(STUDENTS, 80)
    assert got == ["Ada"], f"names_over(students, 80) returned {got!r}"


def test_other_limits():
    """A limit of 70 gives all three names in order; a limit of 100 gives none."""
    names_over = function("names_over")
    assert names_over(STUDENTS, 70) == ["Ada", "Bob", "Cy"], (
        f"names_over(students, 70) returned {names_over(STUDENTS, 70)!r}"
    )
    assert names_over(STUDENTS, 100) == [], (
        f"names_over(students, 100) returned {names_over(STUDENTS, 100)!r}"
    )
