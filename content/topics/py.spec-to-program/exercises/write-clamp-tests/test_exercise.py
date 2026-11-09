from pathlib import Path

from checks import function


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_clamp():
    """clamp keeps a value inside the range: 5 stays 5, -3 becomes 0, 42 becomes 10, 10 stays 10."""
    clamp = function("clamp")
    for n, expected in [(5, 5), (-3, 0), (42, 10), (10, 10), (0, 0)]:
        got = clamp(n, 0, 10)
        assert got == expected, f"clamp({n}, 0, 10) returned {got!r}, not {expected!r}"
    assert clamp(7.5, 1, 7) == 7, "clamp(7.5, 1, 7) should be 7"


def test_tests():
    """test_clamp has 4 or more asserts, passes, and fails when clamp just returns n."""
    assert count_asserts() >= 4, f"found {count_asserts()} asserts; the spec asks for at least 4"
    test = function("test_clamp")
    test()
    import solution

    original = solution.clamp
    solution.clamp = lambda n, low, high: n
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.clamp = original
    assert caught, "test_clamp still passed when clamp returned n unchanged"
