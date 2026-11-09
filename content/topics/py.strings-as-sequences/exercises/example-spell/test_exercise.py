from checks import run, run_with


def test_python():
    """Takes python apart: first p, last n, middle yth, then one line per character."""
    assert run() == (
        "First: p\nLast: n\nMiddle: yth\n0 p\n1 y\n2 t\n3 h\n4 o\n5 n\nLength: 6\n"
    )


def test_loop():
    """Works for the word loop too."""
    assert run_with({"word": "loop"}) == (
        "First: l\nLast: p\nMiddle: oop\n0 l\n1 o\n2 o\n3 p\nLength: 4\n"
    )
