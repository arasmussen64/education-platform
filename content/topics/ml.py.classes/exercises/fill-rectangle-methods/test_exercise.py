from checks import function, run


def test_three_by_four():
    """Prints 12, then 14."""
    printed = run()
    assert printed == "12\n14\n", f"Your program printed:\n{printed}"


def test_another_rectangle():
    """A 5 by 2 rectangle has area 10 and perimeter 14."""
    Rectangle = function("Rectangle")
    other = Rectangle(5, 2)
    assert other.area() == 10
    assert other.perimeter() == 14
