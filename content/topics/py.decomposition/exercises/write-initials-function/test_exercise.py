from checks import function, printed


def test_three_names():
    """initials("Ada King Lovelace") returns AKL."""
    initials = function("initials")
    assert initials("Ada King Lovelace") == "AKL", (
        f'initials("Ada King Lovelace") returned {initials("Ada King Lovelace")!r}'
    )


def test_other_names():
    """initials("Grace Hopper") returns GH, and initials("Guido") returns G."""
    initials = function("initials")
    assert initials("Grace Hopper") == "GH", (
        f'initials("Grace Hopper") returned {initials("Grace Hopper")!r}'
    )
    assert initials("Guido") == "G", f'initials("Guido") returned {initials("Guido")!r}'


def test_docstring_and_quiet():
    """initials has a docstring and prints nothing."""
    initials = function("initials")
    assert (initials.__doc__ or "").strip() != "", "Give initials a docstring"
    assert printed(initials, "Ada King") == "", "initials should return, not print"
