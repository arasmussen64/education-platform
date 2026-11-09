from pathlib import Path

from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.

CSV = "name,city\nAda,London\nBob,Leeds\n"


def test_column():
    """column_values gives the cities in order, without the header."""
    Path("c.csv").write_text(CSV, encoding="utf-8")
    assert function("column_values")("c.csv", "city") == ["London", "Leeds"]


def test_other_column_and_empty():
    """Any column works, and a file with only a header gives []."""
    Path("c.csv").write_text(CSV, encoding="utf-8")
    Path("h.csv").write_text("name,city\n", encoding="utf-8")
    column_values = function("column_values")
    assert column_values("c.csv", "name") == ["Ada", "Bob"]
    assert column_values("h.csv", "name") == []
