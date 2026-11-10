from checks import function, run


def test_the_output():
    """Prints the record, then 90.0."""
    printed = run()
    assert printed == "Student(name='Ada', grades=[80, 90, 100])\n90.0\n", f"Your program printed:\n{printed}"


def test_the_dataclass():
    """Student is a dataclass: equal records compare equal, and average works for other grades."""
    Student = function("Student")
    assert Student("Bob", [70, 75]) == Student("Bob", [70, 75])
    assert Student("Bob", [70, 75]).average() == 72.5
    assert Student.__dataclass_fields__.keys() == {"name", "grades"}
