import importlib
import io
import sys
from contextlib import redirect_stdout

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXPECTED = "4 rows\n{'count': 3, 'mean': 20.0, 'min': 12, 'max': 30}\nscore: count=3 mean=20.0 min=12 max=30\n2 passed\n"
OTHER = '{"id": 1, "x": 2}\n\n{"id": 2}\n{"id": 3, "x": 4}\n'


def load_solution():
    """The learner's module, imported fresh, with its prints swallowed."""
    sys.modules.pop("solution", None)
    importlib.invalidate_caches()
    with redirect_stdout(io.StringIO()):
        return importlib.import_module("solution")


def learner_tests(module):
    return [getattr(module, name) for name in dir(module) if name.startswith("test_")]


def catches(module, bug):
    """Whether any of the learner's tests fails once Dataset.summary is replaced by bug."""
    if not hasattr(getattr(module, "Dataset", None), "summary"):
        raise AssertionError("Define a class called Dataset with a summary method.")
    original = module.Dataset.summary
    module.Dataset.summary = bug
    try:
        for test in learner_tests(module):
            try:
                test()
            except Exception:
                return True
        return False
    finally:
        module.Dataset.summary = original


def other_dataset():
    with open("other.jsonl", "w") as f:
        f.write(OTHER)
    return function("Dataset")("other.jsonl")


def test_the_output():
    """Prints the row count, the summary, the report line and 2 passed."""
    assert run() == EXPECTED


def test_rows_is_a_lazy_generator():
    """Making a Dataset reads nothing; rows() hands out one record per next() and skips blank lines."""
    Dataset = function("Dataset")
    Dataset("no-such-file.jsonl")
    rows = other_dataset().rows()
    assert next(rows) == {"id": 1, "x": 2}
    assert list(rows) == [{"id": 2}, {"id": 3, "x": 4}]


def test_column_and_summary():
    """column skips records without the key; summary has count, mean, min and max, and a zero count for a missing column."""
    ds = other_dataset()
    assert list(ds.column("x")) == [2, 4]
    assert ds.summary("x") == {"count": 2, "mean": 3.0, "min": 2, "max": 4}
    assert ds.summary("nope") == {"count": 0, "mean": None, "min": None, "max": None}


def test_the_report():
    """write_report writes the one-line report to the path it's given."""
    other_dataset().write_report("x", "other-report.txt")
    with open("other-report.txt") as f:
        assert f.read() == "x: count=2 mean=3.0 min=2 max=4\n"


def test_the_tests_catch_a_wrong_summary():
    """At least two tests, all passing, that fail for a summary that counts every row, and for one that crashes on a column no record has."""
    module = load_solution()
    assert len(learner_tests(module)) >= 2
    for test in learner_tests(module):
        test()

    def counts_every_row(self, name):
        rows = list(self.rows())
        values = [row[name] for row in rows if name in row]
        return {"count": len(rows), "mean": sum(values) / len(rows), "min": min(values), "max": max(values)}

    def crashes_on_empty(self, name):
        values = list(self.column(name))
        return {"count": len(values), "mean": sum(values) / len(values), "min": min(values), "max": max(values)}

    assert catches(module, counts_every_row)
    assert catches(module, crashes_on_empty)
