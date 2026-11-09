from checks import function


def test_average():
    """average([2, 4]) is 3, and average([1, 2, 3, 4]) is 2.5."""
    average = function("average")
    assert average([2, 4]) == 3, f"average([2, 4]) returned {average([2, 4])!r}"
    assert average([1, 2, 3, 4]) == 2.5, f"average([1, 2, 3, 4]) returned {average([1, 2, 3, 4])!r}"


def test_hypotenuse():
    """hypotenuse(3, 4) is 5.0, and hypotenuse(5, 12) is 13.0."""
    hypotenuse = function("hypotenuse")
    assert hypotenuse(3, 4) == 5.0, f"hypotenuse(3, 4) returned {hypotenuse(3, 4)!r}"
    assert hypotenuse(5, 12) == 13.0, f"hypotenuse(5, 12) returned {hypotenuse(5, 12)!r}"
