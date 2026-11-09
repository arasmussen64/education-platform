def square_area(side):
    """Return the area of a square with the given side."""
    return side * side


def describe_square(side):
    """Return a sentence giving a square's side and area."""
    return f"A square of side {side} has area {square_area(side)}"
