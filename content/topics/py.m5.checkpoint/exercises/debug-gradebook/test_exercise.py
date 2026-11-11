from checks import function, run


def test_average():
    """average([90, 80]) is 85.0: the total divided by how many scores there are."""
    average = function("average")
    assert average([90, 80]) == 85.0, f"average([90, 80]) returned {average([90, 80])!r}"
    assert average([70]) == 70.0, f"average([70]) returned {average([70])!r}"


def test_letter_boundaries():
    """90 is an A, 80 a B, 70 a C, 60 a D, and 59 an F."""
    letter_grade = function("letter_grade")
    for value, expected in [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (59, "F")]:
        got = letter_grade(value)
        assert got == expected, f"letter_grade({value}) returned {got!r}, not {expected!r}"


def test_leaves_list_alone():
    """report_lines leaves the list it's given with all its students."""
    students = [{"name": "X", "scores": [50]}, {"name": "Y", "scores": [100]}]
    function("report_lines")(students)
    assert len(students) == 2, f"after report_lines the list has {len(students)} students"


def test_program():
    """Prints Ada's and Bob's lines, then Students: 2."""
    got = run()
    assert got == "Ada: 85.0 (B)\nBob: 65.0 (D)\nStudents: 2\n", f"Your program printed:\n{got}"
