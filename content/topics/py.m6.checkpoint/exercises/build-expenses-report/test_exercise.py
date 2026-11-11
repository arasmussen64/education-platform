from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).

REPORT = "food: 61.70\ntravel: 55.75\nRows: 6\nBad rows: 2\nTotal: 117.45\n"


def sample_rows():
    """A fresh copy of the rows the sample file holds, so every test starts from the same place."""
    return [
        {"date": "2026-02-01", "category": "food", "cost": "12.20"},
        {"date": "2026-02-01", "category": "travel", "cost": "40"},
        {"date": "2026-02-02", "category": "food", "cost": "abc"},
        {"date": "2026-02-02", "category": "food", "cost": "49.50"},
        {"date": "2026-02-03", "category": "rent", "cost": ""},
        {"date": "2026-02-03", "category": "travel", "cost": "15.75"},
    ]


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def lines_of(path):
    """The file's lines, without their line breaks.

    Files are compared line by line, not character by character, so a report
    whose last line has no line break after it still passes: the spec says
    "one per line" and nothing about how the file ends.
    """
    return Path(path).read_text(encoding="utf-8").splitlines()


def test_read_rows():
    """read_rows gives one dictionary per data row, with the header as keys and every value text."""
    Path("rr.csv").write_text("date,category,cost\n2026-02-01,food,12.20\n2026-02-03,rent,\n", encoding="utf-8")
    assert function("read_rows")("rr.csv") == [
        {"date": "2026-02-01", "category": "food", "cost": "12.20"},
        {"date": "2026-02-03", "category": "rent", "cost": ""},
    ]


def test_cost_of():
    """cost_of: 12.2 for "12.20", 40.0 for "40", None for "abc" and for a blank cost."""
    cost_of = function("cost_of")
    rows = sample_rows()
    assert cost_of(rows[0]) == 12.2
    assert cost_of(rows[1]) == 40.0
    assert cost_of(rows[2]) is None
    assert cost_of(rows[4]) is None


def test_good_rows():
    """good_rows keeps the four rows whose cost is a number, in order, and gives [] for none."""
    good_rows = function("good_rows")
    rows = sample_rows()
    assert good_rows(rows) == [rows[0], rows[1], rows[3], rows[5]]
    assert good_rows([rows[2], rows[4]]) == []
    assert good_rows([]) == []


def test_totals_by_category():
    """totals_by_category adds the good costs per category, in order of first appearance."""
    totals = function("totals_by_category")(sample_rows())
    assert list(totals) == ["food", "travel"]
    assert abs(totals["food"] - 61.7) < 0.001
    assert abs(totals["travel"] - 55.75) < 0.001
    assert function("totals_by_category")([]) == {}


def test_report_lines():
    """report_lines gives a line per category with two decimals, then Rows, Bad rows and Total."""
    report_lines = function("report_lines")
    assert report_lines(sample_rows()) == REPORT.splitlines()
    assert report_lines([]) == ["Rows: 0", "Bad rows: 0", "Total: 0.00"]


def test_write_report():
    """write_report puts every line in the file, one per line, replacing what was there."""
    write_report = function("write_report")
    write_report("wr.txt", ["old"])
    write_report("wr.txt", ["a: 1.00", "Rows: 1"])
    assert lines_of("wr.txt") == ["a: 1.00", "Rows: 1"]


def test_leaves_data_alone():
    """No function changes the rows list it's given."""
    rows = sample_rows()
    function("good_rows")(rows)
    function("totals_by_category")(rows)
    function("report_lines")(rows)
    assert rows == sample_rows()


def test_docstrings():
    """Every function has a docstring."""
    names = (
        "read_rows",
        "cost_of",
        "good_rows",
        "totals_by_category",
        "report_lines",
        "write_report",
        "main",
    )
    for name in names:
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_expenses has 4 or more asserts, passes, and fails when cost_of calls every row worth 1.0."""
    assert count_asserts() >= 4
    test = function("test_expenses")
    test()
    import solution

    original = solution.cost_of
    solution.cost_of = lambda row: 1.0
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.cost_of = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report, and writes expenses.txt."""
    assert run() == "expenses: all checks passed\n" + REPORT
    assert lines_of("expenses.txt") == REPORT.splitlines()
