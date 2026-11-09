STUDENTS = [
    {"name": "Ada", "scores": [90, 80]},
    {"name": "Bob", "scores": [70, 60]},
]


def average(scores):
    """Return the average of a non-empty list of scores."""
    total = 0
    for score in scores:
        total += score
    return total / len(scores)


def letter_grade(average):
    """Return A for 90 or more, B for 80 or more, C for 70, D for 60, else F."""
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def report_lines(students):
    """Return one line per student; the list given is unchanged."""
    lines = []
    while students:
        student = students.pop(0)
        avg = average(student["scores"])
        lines.append(f"{student['name']}: {avg:.1f} ({letter_grade(avg)})")
    return lines


def main():
    """Print the report, then how many students there are."""
    for line in report_lines(STUDENTS):
        print(line)
    print(f"Students: {len(STUDENTS)}")


if __name__ == "__main__":
    main()
