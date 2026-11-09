STUDENTS = [
    {"name": "Ada", "scores": [95, 88, 92]},
    {"name": "Bob", "scores": [72, 65, 80]},
    {"name": "Cy", "scores": [85, 90, 78]},
]


def average(scores):
    """Return the average of the scores."""
    total = 0
    for score in scores:
        total += score
    return total / len(scores)


def letter_grade(average):
    """Return the letter grade."""
    if average > 90:
        return "A"
    if average > 80:
        return "B"
    if average > 70:
        return "C"
    if average > 60:
        return "D"
    return "F"


def best_student(students):
    """Return the name of the best student."""
    best = students[0]
    for student in students:
        if average(student["scores"]) > average(best["scores"]):
            best = student
    return best["name"]


def report_lines(students):
    """Return the report lines."""
    lines = []
    for student in students:
        avg = average(student["scores"])
        lines.append(f"{student['name']}: {avg:.1f} ({letter_grade(avg)})")
    lines.append(f"Best: {best_student(students)}")
    return lines


def test_gradebook():
    assert letter_grade(95) == "A"
    assert letter_grade(85) == "B"
    assert letter_grade(59) == "F"
    assert best_student(STUDENTS) == "Ada"
    print("gradebook: all checks passed")


def main():
    """Print the report."""
    for line in report_lines(STUDENTS):
        print(line)


if __name__ == "__main__":
    test_gradebook()
    main()
