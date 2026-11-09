from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def entry(age, member):
    return run(f"{age}\n{member}\n")


def test_free_entry():
    """Under 5s and over 70s get in free, members or not."""
    assert entry(3, "no") == "Entry: $0.00\n"
    assert entry(72, "yes") == "Entry: $0.00\n"
    assert entry(70, "no") == "Entry: $0.00\n"


def test_young_visitors():
    """Ages 5 to 17 pay $4.00, or $2.00 as members."""
    assert entry(10, "no") == "Entry: $4.00\n"
    assert entry(10, "yes") == "Entry: $2.00\n"
    assert entry(5, "no") == "Entry: $4.00\n"
    assert entry(17, "no") == "Entry: $4.00\n"


def test_adults():
    """Adults pay $12.00, or $6.00 as members."""
    assert entry(30, "no") == "Entry: $12.00\n"
    assert entry(30, "yes") == "Entry: $6.00\n"
    assert entry(18, "no") == "Entry: $12.00\n"
