from pathlib import Path

from checks import function

CSV = "item,region,amount\npen,north,2.5\nbook,south,10\nlamp,north,150\n"


def test_matching_rows():
    """rows_where picks the two northern rows, as dictionaries, in order."""
    Path("orders.csv").write_text(CSV, encoding="utf-8")
    got = function("rows_where")("orders.csv", "region", "north")
    assert got == [
        {"item": "pen", "region": "north", "amount": "2.5"},
        {"item": "lamp", "region": "north", "amount": "150"},
    ], f"rows_where returned {got!r}"


def test_no_match_and_other_field():
    """No match gives [], and any field can be used."""
    Path("orders.csv").write_text(CSV, encoding="utf-8")
    rows_where = function("rows_where")
    assert rows_where("orders.csv", "region", "east") == []
    assert rows_where("orders.csv", "item", "book") == [
        {"item": "book", "region": "south", "amount": "10"}
    ]
