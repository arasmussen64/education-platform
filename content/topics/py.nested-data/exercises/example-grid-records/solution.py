grid = [
    [1, 2, 3],
    [4, 5, 6],
]
print(grid[1][2])
for row in grid:
    print(row)
for row in grid:
    for cell in row:
        print(cell, end=" ")
    print()

students = [
    {"name": "Ada", "score": 91},
    {"name": "Bob", "score": 78},
]
for student in students:
    print(f"{student['name']}: {student['score']}")
