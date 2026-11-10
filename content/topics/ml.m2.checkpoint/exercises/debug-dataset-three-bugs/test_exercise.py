from checks import function, run

EXPECTED = "4 rows\n{'count': 3, 'mean': 20.0, 'min': 18.5, 'max': 21.5}\ntemperature: count=3 mean=20.0 min=18.5 max=21.5\n"


def test_the_output():
    """Prints the row count, the summary and the report line."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_records():
    """Works for other records: a column present in two of three rows."""
    Dataset = function("Dataset")
    with open("other.jsonl", "w") as f:
        f.write('{"temperature": 1}\n{"x": 0}\n{"temperature": 3}\n')
    ds = Dataset("other.jsonl")
    assert ds.summary("temperature") == {"count": 2, "mean": 2.0, "min": 1, "max": 3}, (
        f"With temperatures 1 and 3 in three rows, summary gave {ds.summary('temperature')}"
    )
    ds.write_report("temperature", "other-report.txt")
    with open("other-report.txt") as f:
        report = f.read()
    assert report == "temperature: count=2 mean=2.0 min=1 max=3\n", f"The report for that file reads:\n{report}"
