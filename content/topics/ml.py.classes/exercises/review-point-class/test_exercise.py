from checks import function, run


def test_three_four():
    """Prints 5.0."""
    assert run() == "5.0\n"


def test_other_points():
    """Point(6, 8) is 10.0 from the origin, and the attributes are x and y."""
    Point = function("Point")
    p = Point(6, 8)
    assert p.x == 6
    assert p.y == 8
    assert p.distance_from_origin() == 10.0
