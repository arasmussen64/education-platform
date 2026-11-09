from checks import function, run

STUDENTS = [{"name": "Ada", "score": 91}, {"name": "Bob", "score": 78}]
GRID = [[1, 2, 3], [4, 5, 6]]


def test_program():
    """Prints the names, the best name, and the cell at row 1, column 2."""
    got = run()
    assert got == "['Ada', 'Bob']\nAda\n6\n", f"Your program printed:\n{got}"


def test_names_of():
    """names_of returns just the names."""
    got = function("names_of")(STUDENTS)
    assert got == ["Ada", "Bob"], f"names_of returned {got!r}"


def test_best_name():
    """best_name returns Ada, the name of the top scorer."""
    got = function("best_name")(STUDENTS)
    assert got == "Ada", f"best_name returned {got!r}"


def test_cell():
    """cell(grid, 0, 2) is 3 and cell(grid, 1, 0) is 4: row first, then column."""
    cell = function("cell")
    assert cell(GRID, 0, 2) == 3, f"cell(grid, 0, 2) returned {cell(GRID, 0, 2)!r}"
    assert cell(GRID, 1, 0) == 4, f"cell(grid, 1, 0) returned {cell(GRID, 1, 0)!r}"
