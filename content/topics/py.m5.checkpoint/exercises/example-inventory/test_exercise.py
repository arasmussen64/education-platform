from checks import function, run


def test_program():
    """Run directly, the tests pass and the report prints."""
    assert run() == (
        "inventory: all checks passed\n"
        "pens: $60.00 (ok)\nnotebooks: $20.00 (low)\nstaplers: $0.00 (out)\n"
        "Most valuable: pens\n"
    )


def test_pieces():
    """status has its boundaries right, and report_lines leaves the items unchanged."""
    status = function("status")
    assert status(0) == "out" and status(5) == "low" and status(6) == "ok"
    items = [{"name": "a", "quantity": 1, "price": 2.0}]
    function("report_lines")(items)
    assert items == [{"name": "a", "quantity": 1, "price": 2.0}]
