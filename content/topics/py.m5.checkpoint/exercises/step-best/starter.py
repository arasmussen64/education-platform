# The data: one record per student
STUDENTS = [
    {"name": "Ada", "scores": [95, 88, 92]},
    {"name": "Bob", "scores": [72, 65, 80]},
    {"name": "Cy", "scores": [85, 90, 78]},
]


# A number from a list, and a grade from a number
def average(scores):
    """Return the average of a non-empty list of scores."""
    total = 0
    for score in scores:
        total += score
    return total / len(scores)


def letter_grade(average):
    """Return A, B, C, D or F for an average."""
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


# The best record
def best_student(students):
    """Return the name of the student with the highest average, the first if two tie."""
    best = ...
    for student in students:
        if average(student["scores"]) > average(...["scores"]):
            best = student
    return best[...]


# The report, as lines of text
def report_lines(students):
    """Return one line per student, like 'Ada: 91.7 (A)', then 'Best: Ada'."""
    lines = []
    for student in students:
        avg = average(student["scores"])
        lines.append(f"{student['name']}: {avg:.1f} ({letter_grade(avg)})")
    lines.append(f"Best: {best_student(students)}")
    return lines


# The tests
def test_gradebook():
    assert average([90, 80]) == 85.0
    assert letter_grade(90) == "A"
    assert letter_grade(89.9) == "B"
    assert letter_grade(59) == "F"
    assert best_student(STUDENTS) == "Ada"
    print("gradebook: all checks passed")


# The program
def main():
    """Print the report."""
    for line in report_lines(STUDENTS):
        print(line)


if __name__ == "__main__":
    test_gradebook()
    main()
