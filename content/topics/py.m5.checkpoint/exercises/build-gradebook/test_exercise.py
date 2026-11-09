from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def sample():
    """A fresh copy of the data, so every test starts from the same place."""
    return [
        {"name": "Ada", "scores": [95, 88, 92]},
        {"name": "Bob", "scores": [72, 65, 80]},
        {"name": "Cy", "scores": [85, 90, 78]},
    ]


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_average():
    """average([95, 88, 92]) is about 91.67, and average([70]) is 70.0."""
    average = function("average")
    assert abs(average([95, 88, 92]) - 91.6667) < 0.001
    assert average([70]) == 70.0
    assert average([60, 80]) == 70.0


def test_letter_grade():
    """letter_grade: A at 90, B at 89.9 and 80, C at 70, D at 60, F below."""
    letter_grade = function("letter_grade")
    assert letter_grade(90) == "A"
    assert letter_grade(95.5) == "A"
    assert letter_grade(89.9) == "B"
    assert letter_grade(80) == "B"
    assert letter_grade(70) == "C"
    assert letter_grade(60) == "D"
    assert letter_grade(59.9) == "F"
    assert letter_grade(0) == "F"


def test_best_student():
    """best_student picks the highest average, the first of two who tie."""
    best_student = function("best_student")
    assert best_student(sample()) == "Ada"
    tie = [{"name": "X", "scores": [80]}, {"name": "Y", "scores": [80]}]
    assert best_student(tie) == "X"
    assert best_student([{"name": "Solo", "scores": [50]}]) == "Solo"


def test_report_lines():
    """report_lines gives one formatted line per student, then the Best line."""
    report_lines = function("report_lines")
    assert report_lines(sample()) == [
        "Ada: 91.7 (A)",
        "Bob: 72.3 (C)",
        "Cy: 84.3 (B)",
        "Best: Ada",
    ]
    assert report_lines([{"name": "Dee", "scores": [100]}]) == ["Dee: 100.0 (A)", "Best: Dee"]


def test_leaves_data_alone():
    """No function changes the students list or any scores list."""
    students = sample()
    function("report_lines")(students)
    function("best_student")(students)
    function("average")(students[0]["scores"])
    assert students == sample()


def test_docstrings():
    """Every function has a docstring."""
    for name in ("average", "letter_grade", "best_student", "report_lines", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_gradebook has 4 or more asserts, passes, and fails when letter_grade always says A."""
    assert count_asserts() >= 4
    test = function("test_gradebook")
    test()
    import solution

    original = solution.letter_grade
    solution.letter_grade = lambda average: "A"
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.letter_grade = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report."""
    assert run() == (
        "gradebook: all checks passed\nAda: 91.7 (A)\nBob: 72.3 (C)\nCy: 84.3 (B)\nBest: Ada\n"
    )
