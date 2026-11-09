from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).

REPORT = "hill: 12.5\nvalley: 7.5\nRows: 5\nBad rows: 1\nTotal: 20.0\n"


def sample_rows():
    """A fresh copy of the rows the sample file holds, so every test starts from the same place."""
    return [
        {"day": "1", "station": "hill", "mm": "4.5"},
        {"day": "1", "station": "valley", "mm": "2.0"},
        {"day": "2", "station": "hill", "mm": "n/a"},
        {"day": "2", "station": "valley", "mm": "5.5"},
        {"day": "3", "station": "hill", "mm": "8.0"},
    ]


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_read_rows():
    """read_rows gives one dictionary per data row, with the header as keys and every value text."""
    Path("rr.csv").write_text("day,station,mm\n1,hill,4.5\n2,hill,\n", encoding="utf-8")
    assert function("read_rows")("rr.csv") == [
        {"day": "1", "station": "hill", "mm": "4.5"},
        {"day": "2", "station": "hill", "mm": ""},
    ]


def test_mm_of():
    """mm_of: 4.5 for "4.5", 2.0 for "2.0", None for "n/a" and for a blank reading."""
    mm_of = function("mm_of")
    rows = sample_rows()
    assert mm_of(rows[0]) == 4.5
    assert mm_of(rows[1]) == 2.0
    assert mm_of(rows[2]) is None
    assert mm_of({"day": "9", "station": "hill", "mm": ""}) is None


def test_good_rows():
    """good_rows keeps the four rows whose reading is a number, in order, and gives [] for none."""
    good_rows = function("good_rows")
    rows = sample_rows()
    assert good_rows(rows) == [rows[0], rows[1], rows[3], rows[4]]
    assert good_rows([rows[2]]) == []
    assert good_rows([]) == []


def test_totals_by_station():
    """totals_by_station adds the good readings per station, in order of first appearance."""
    totals_by_station = function("totals_by_station")
    totals = totals_by_station(sample_rows())
    assert totals == {"hill": 12.5, "valley": 7.5}
    assert list(totals) == ["hill", "valley"]
    assert totals_by_station([]) == {}


def test_report_lines():
    """report_lines gives a line per station with one decimal, then Rows, Bad rows and Total."""
    report_lines = function("report_lines")
    assert report_lines(sample_rows()) == REPORT.splitlines()
    assert report_lines([]) == ["Rows: 0", "Bad rows: 0", "Total: 0.0"]


def test_write_report():
    """write_report puts every line in the file, one per line, replacing what was there."""
    write_report = function("write_report")
    write_report("wr.txt", ["old"])
    write_report("wr.txt", ["a: 1.0", "Rows: 1"])
    assert Path("wr.txt").read_text(encoding="utf-8") == "a: 1.0\nRows: 1\n"


def test_leaves_data_alone():
    """No function changes the rows list it's given."""
    rows = sample_rows()
    function("good_rows")(rows)
    function("totals_by_station")(rows)
    function("report_lines")(rows)
    assert rows == sample_rows()


def test_docstrings():
    """Every function has a docstring."""
    names = (
        "read_rows",
        "mm_of",
        "good_rows",
        "totals_by_station",
        "report_lines",
        "write_report",
        "main",
    )
    for name in names:
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_rainfall has 4 or more asserts, passes, and fails when mm_of calls every row worth 1.0."""
    assert count_asserts() >= 4
    test = function("test_rainfall")
    test()
    import solution

    original = solution.mm_of
    solution.mm_of = lambda row: 1.0
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.mm_of = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report, and writes rainfall.txt."""
    assert run() == "rainfall: all checks passed\n" + REPORT
    assert Path("rainfall.txt").read_text(encoding="utf-8") == REPORT
