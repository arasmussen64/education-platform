def names_of(students):
    """Return the names."""
    names = []
    for student in students:
        names.append(student["name"])
    return names


def oldest(students):
    """Return the name of the oldest student."""
    best = students[0]
    for student in students:
        if student["age"] > best["age"]:
            best = student
    return best["name"]


def average_age(students):
    """Return the average age."""
    total = 0
    for student in students:
        total += student["age"]
    return total / len(students)


def column(grid, index):
    """Return one column of the grid."""
    return grid[index]


def main():
    students = [
        {"name": "Ada", "age": 36},
        {"name": "Bob", "age": 41},
        {"name": "Cy", "age": 29},
    ]
    grid = [[1, 2, 3], [4, 5, 6]]
    print(f"Names: {names_of(students)}")
    print(f"Oldest: {oldest(students)}")
    print(f"Average age: {average_age(students):.2f}")
    print(f"Column 1: {column(grid, 1)}")


main()
