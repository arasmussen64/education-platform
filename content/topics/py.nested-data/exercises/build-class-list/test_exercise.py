from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

STUDENTS = [
    {"name": "Ada", "age": 36},
    {"name": "Bob", "age": 41},
    {"name": "Cy", "age": 29},
]


def test_names_of():
    """names_of gives the names in order, and [] for no students."""
    names_of = function("names_of")
    assert names_of(STUDENTS) == ["Ada", "Bob", "Cy"]
    assert names_of([]) == []


def test_oldest():
    """oldest gives Bob here, and the first of two who tie."""
    oldest = function("oldest")
    assert oldest(STUDENTS) == "Bob"
    assert oldest([{"name": "X", "age": 5}, {"name": "Y", "age": 5}]) == "X"


def test_average_age():
    """average_age is 35.333... here and 1.5 for ages 1 and 2."""
    average_age = function("average_age")
    assert abs(average_age(STUDENTS) - 35.3333) < 0.001
    assert average_age([{"name": "X", "age": 1}, {"name": "Y", "age": 2}]) == 1.5


def test_column():
    """column picks one value from each row, top to bottom."""
    column = function("column")
    assert column([[1, 2, 3], [4, 5, 6]], 1) == [2, 5]
    assert column([[1, 2, 3], [4, 5, 6]], 0) == [1, 4]
    assert column([], 0) == []


def test_program():
    """Running the program prints the four lines."""
    assert run() == "Names: ['Ada', 'Bob', 'Cy']\nOldest: Bob\nAverage age: 35.33\nColumn 1: [2, 5]\n"
