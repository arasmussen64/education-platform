from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the first line, then 13.0."""
    assert run() == "Line(item='pen', quantity=3, unit_price=1.5)\n13.0\n"


def test_the_record():
    """Line is a dataclass with the three fields; equal lines compare equal; total multiplies."""
    Line = function("Line")
    assert Line.__dataclass_fields__.keys() == {"item", "quantity", "unit_price"}
    assert Line("a", 1, 2.0) == Line("a", 1, 2.0)
    assert Line("tape", 4, 0.75).total() == 3.0


def test_order_total_and_its_hints():
    """order_total adds the lines up, is 0 for no lines, and is hinted to return a float."""
    Line = function("Line")
    order_total = function("order_total")
    assert order_total([Line("a", 2, 1.5), Line("b", 1, 2.0)]) == 5.0
    assert order_total([]) == 0
    assert order_total.__annotations__.get("return") is float
