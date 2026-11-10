from checks import function, run


def test_the_output():
    """Prints the three temperatures, then an empty list."""
    printed = run()
    assert printed == "[18.5, 21.5, 20.0]\n[]\n", f"Your program printed:\n{printed}"


def test_other_column():
    """column skips records without the key and yields one value per next()."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\n{"b": 2}\n{"a": 3}\n')
    values = Dataset("two.jsonl").column("a")
    assert next(values) == 1
    assert list(values) == [3]
