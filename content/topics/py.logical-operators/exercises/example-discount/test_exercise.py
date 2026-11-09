from checks import run


def test_child():
    """A child who isn't a member pays $6."""
    assert run("8\nno\n") == "Price: $6\n"


def test_adult_member():
    """An adult member pays $8: full price with $2 off."""
    assert run("30\nyes\n") == "Price: $8\n"


def test_senior_member():
    """A senior member pays $6: the reduced price, with nothing more off."""
    assert run("70\nyes\n") == "Price: $6\n"


def test_adult():
    """An adult who isn't a member pays $10."""
    assert run("30\nno\n") == "Price: $10\n"
