from pathlib import Path

from checks import function

CSV = "item,amount,quantity\npen,2.5,10\nbook,10,2\n"


def test_amount_total():
    """total_of("t.csv", "amount") is 12.5."""
    Path("t.csv").write_text(CSV, encoding="utf-8")
    got = function("total_of")("t.csv", "amount")
    assert got == 12.5, f"total_of returned {got!r} for the amount column"


def test_other_column():
    """total_of("t.csv", "quantity") is 12.0: the field parameter picks the column."""
    Path("t.csv").write_text(CSV, encoding="utf-8")
    got = function("total_of")("t.csv", "quantity")
    assert got == 12.0, f"total_of returned {got!r} for the quantity column"
