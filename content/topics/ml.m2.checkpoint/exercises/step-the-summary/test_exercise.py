from checks import function, run


def test_the_output():
    """Prints the temperature summary, then the empty one."""
    printed = run()
    assert printed == (
        "{'count': 3, 'mean': 20.0, 'min': 18.5, 'max': 21.5}\n"
        "{'count': 0, 'mean': None, 'min': None, 'max': None}\n"
    ), f"Your program printed:\n{printed}"


def test_other_column():
    """The mean divides by the number of values, not rows."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\n{"b": 2}\n{"a": 3}\n')
    assert Dataset("two.jsonl").summary("a") == {"count": 2, "mean": 2.0, "min": 1, "max": 3}
