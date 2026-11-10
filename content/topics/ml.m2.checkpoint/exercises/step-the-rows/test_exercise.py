from checks import function, run


def test_the_output():
    """Prints the first record, then 3 more."""
    printed = run()
    assert printed == "{'sensor': 'a', 'temperature': 18.5}\n3 more\n", f"Your program printed:\n{printed}"


def test_rows_is_a_generator():
    """rows() gives one record per next()."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\n\n{"a": 2}\n')
    rows = Dataset("two.jsonl").rows()
    assert next(rows) == {"a": 1}
    assert next(rows) == {"a": 2}
