from checks import function, run


def test_the_output():
    """Prints the report line, then 1 passed."""
    printed = run()
    assert printed == "temperature: count=3 mean=20.0 min=18.5 max=21.5\n1 passed\n", f"Your program printed:\n{printed}"


def test_other_report():
    """write_report writes the one-line report for another column and file."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\n{"b": 2}\n{"a": 3}\n')
    Dataset("two.jsonl").write_report("a", "two-report.txt")
    with open("two-report.txt") as f:
        assert f.read() == "a: count=2 mean=2.0 min=1 max=3\n"
