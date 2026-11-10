from checks import function, run


def test_the_output():
    """Prints 10.0."""
    printed = run()
    assert printed == "10.0\n", f"Your program printed:\n{printed}"


def test_the_hints():
    """area's parameters and return value are hinted as float."""
    area = function("area")
    assert area.__annotations__ == {"width": float, "height": float, "return": float}, (
        f"The hints on area are {area.__annotations__}"
    )
