from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).

REPORT = "north: 150.50\nsouth: 80.00\neast: 45.25\nRows: 6\nBad rows: 2\nTotal: 275.75\n"


def sample_rows():
    """A fresh copy of the rows the sample file holds, so every test starts from the same place."""
    return [
        {"date": "2026-01-03", "region": "north", "amount": "120.50"},
        {"date": "2026-01-03", "region": "south", "amount": "80"},
        {"date": "2026-01-04", "region": "north", "amount": "abc"},
        {"date": "2026-01-04", "region": "east", "amount": "45.25"},
        {"date": "2026-01-05", "region": "south", "amount": ""},
        {"date": "2026-01-05", "region": "north", "amount": "30"},
    ]


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_read_rows():
    """read_rows gives one dictionary per data row, with the header as keys and every value text."""
    Path("rr.csv").write_text(
        "date,region,amount\n2026-01-03,north,120.50\n2026-01-05,south,\n", encoding="utf-8"
    )
    assert function("read_rows")("rr.csv") == [
        {"date": "2026-01-03", "region": "north", "amount": "120.50"},
        {"date": "2026-01-05", "region": "south", "amount": ""},
    ]


def test_amount_of():
    """amount_of: 120.5 for "120.50", 80.0 for "80", None for "abc" and for a blank amount."""
    amount_of = function("amount_of")
    rows = sample_rows()
    assert amount_of(rows[0]) == 120.5
    assert amount_of(rows[1]) == 80.0
    assert amount_of(rows[2]) is None
    assert amount_of(rows[4]) is None


def test_good_rows():
    """good_rows keeps the four rows whose amount is a number, in order, and gives [] for none."""
    good_rows = function("good_rows")
    rows = sample_rows()
    assert good_rows(rows) == [rows[0], rows[1], rows[3], rows[5]]
    assert good_rows([rows[2], rows[4]]) == []
    assert good_rows([]) == []


def test_totals_by_region():
    """totals_by_region adds the good amounts per region, in order of first appearance."""
    totals_by_region = function("totals_by_region")
    totals = totals_by_region(sample_rows())
    assert totals == {"north": 150.5, "south": 80.0, "east": 45.25}
    assert list(totals) == ["north", "south", "east"]
    assert totals_by_region([]) == {}


def test_report_lines():
    """report_lines gives a line per region with two decimals, then Rows, Bad rows and Total."""
    report_lines = function("report_lines")
    assert report_lines(sample_rows()) == REPORT.splitlines()
    assert report_lines([]) == ["Rows: 0", "Bad rows: 0", "Total: 0.00"]


def test_write_report():
    """write_report puts every line in the file, one per line, replacing what was there."""
    write_report = function("write_report")
    write_report("wr.txt", ["old"])
    write_report("wr.txt", ["a: 1.00", "Rows: 1"])
    assert Path("wr.txt").read_text(encoding="utf-8") == "a: 1.00\nRows: 1\n"


def test_leaves_data_alone():
    """No function changes the rows list it's given."""
    rows = sample_rows()
    function("good_rows")(rows)
    function("totals_by_region")(rows)
    function("report_lines")(rows)
    assert rows == sample_rows()


def test_docstrings():
    """Every function has a docstring."""
    names = (
        "read_rows",
        "amount_of",
        "good_rows",
        "totals_by_region",
        "report_lines",
        "write_report",
        "main",
    )
    for name in names:
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_report has 4 or more asserts, passes, and fails when amount_of calls every row worth 1.0."""
    assert count_asserts() >= 4
    test = function("test_report")
    test()
    import solution

    original = solution.amount_of
    solution.amount_of = lambda row: 1.0
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.amount_of = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report, and writes report.txt."""
    assert run() == "report: all checks passed\n" + REPORT
    assert Path("report.txt").read_text(encoding="utf-8") == REPORT
