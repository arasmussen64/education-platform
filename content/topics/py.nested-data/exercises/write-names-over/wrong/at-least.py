def names_over(students, limit):
    """Return the names of the students whose score is greater than the limit."""
    names = []
    for student in students:
        if student["score"] >= limit:
            names.append(student["name"])
    return names
