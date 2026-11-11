from pathlib import Path

from checks import function, run


def test_program():
    """Running the program prints 2, 12.5 and pen."""
    got = run()
    assert got == "2\n12.5\npen\n", f"Your program printed:\n{got}"


def test_read_rows():
    """read_rows returns every row of the file as a dictionary."""
    Path("r.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    got = function("read_rows")("r.csv")
    assert got == [{"a": "1", "b": "2"}], f"read_rows returned {got!r}"


def test_total_amount():
    """total_amount returns the total of the amounts: 1.5 and 2 make 3.5."""
    got = function("total_amount")([{"amount": "1.5"}, {"amount": "2"}])
    assert got == 3.5, f"total_amount returned {got!r}"
