from checks import function, run


def test_program():
    """Running the program prints 3 x 4: area 12, perimeter 14."""
    got = run()
    assert got == "3 x 4: area 12, perimeter 14\n", f"Your program printed:\n{got}"


def test_perimeter_returns():
    """perimeter(3, 4) returns 14."""
    perimeter = function("perimeter")
    assert perimeter(3, 4) == 14, f"perimeter(3, 4) returned {perimeter(3, 4)!r}"


def test_area_docstring():
    """area has a docstring: the sentence is the first line of its body."""
    doc = function("area").__doc__
    assert doc is not None and doc.strip() != "", (
        "area's docstring must be the first line inside the function"
    )


def test_describe_any_size():
    """describe(2, 2) returns 2 x 2: area 4, perimeter 8."""
    describe = function("describe")
    assert describe(2, 2) == "2 x 2: area 4, perimeter 8", (
        f"describe(2, 2) returned {describe(2, 2)!r}"
    )
