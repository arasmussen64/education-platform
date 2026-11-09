from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

CSV = "item,region,amount\npen,north,2.5\nbook,south,10\nlamp,north,150\nmug,south,8\n"
ROWS = [
    {"item": "pen", "region": "north", "amount": "2.5"},
    {"item": "book", "region": "south", "amount": "10"},
    {"item": "lamp", "region": "north", "amount": "150"},
    {"item": "mug", "region": "south", "amount": "8"},
]


def test_read_rows():
    """read_rows gives one dictionary per data row, with the header as keys."""
    Path("rr.csv").write_text(CSV, encoding="utf-8")
    assert function("read_rows")("rr.csv") == ROWS


def test_total_of():
    """total_of adds a column as numbers: 170.5 for amount."""
    total_of = function("total_of")
    assert total_of(ROWS, "amount") == 170.5
    assert total_of([], "amount") == 0


def test_count_by():
    """count_by counts each value of a field, in order of first appearance."""
    count_by = function("count_by")
    assert count_by(ROWS, "region") == {"north": 2, "south": 2}
    assert count_by(ROWS, "item") == {"pen": 1, "book": 1, "lamp": 1, "mug": 1}


def test_program():
    """Running the program writes sales.csv and prints the three summary lines."""
    assert run() == "Rows: 4\nTotal amount: 170.5\nBy region: {'north': 2, 'south': 2}\n"
    assert Path("sales.csv").read_text(encoding="utf-8") == CSV
