students = [
    {"name": "Ada", "score": 91},
    {"name": "Bob", "score": 78},
]
grid = [[1, 2, 3], [4, 5, 6]]


def names_of(students):
    """Return the names, in order."""
    names = []
    for student in students:
        names.append(student["name"])
    return names


def best_name(students):
    """Return the name of the student with the highest score."""
    best = students[0]
    for student in students:
        if student["score"] > best["score"]:
            best = student
    return best["name"]


def cell(grid, row, col):
    """Return the value at the given row and column."""
    return grid[col][row]


def main():
    print(names_of(students))
    print(best_name(students))
    print(cell(grid, 1, 2))


main()
