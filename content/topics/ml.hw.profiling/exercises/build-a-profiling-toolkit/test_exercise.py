from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == "1001000 2000 2 1 ['branch', 'leaf', 'root']\n['grind']\nTrue\n2.0 4.0\n"


def test_counts_and_hot_spots():
    """Three nested functions have the counts the arithmetic gives; the busiest body is the hot spot; no built-in appears."""
    profile = function("profile")
    call_counts = function("call_counts")
    hot_spots = function("hot_spots")

    def leaf():
        return 1

    def inner():
        total = 0
        for _ in range(4):
            total += leaf()
        return total

    def outer():
        return inner() + inner() + inner()

    def busy():
        total = 0
        for i in range(60_000):
            total += i
        return total

    def both():
        outer()
        return busy()

    _, stats = profile(both)
    counts = call_counts(stats)
    assert counts["leaf"] == 12 and counts["inner"] == 3 and counts["outer"] == 1 and counts["both"] == 1
    assert not any(name.startswith("<method") or name.startswith("<built-in") for name in counts)
    assert hot_spots(stats, 1) == ["busy"] and not any(name.startswith("<method") or name.startswith("<built-in") for name in hot_spots(stats, 20))


def test_peak_bytes():
    """A function that builds and then drops a list of 20,000 floats peaks above 20,000 times 8 bytes, far above its final footprint."""
    peak_bytes = function("peak_bytes")

    def build_and_drop():
        numbers = [float(i) for i in range(20_000)]
        return len(numbers)

    peak = peak_bytes(build_and_drop)
    assert 20_000 * 8 < peak < 20_000 * 200


def test_growth():
    """A linear loop doubles its calls, a quadratic one quadruples them, a logarithmic one barely changes."""
    growth = function("growth")

    def mark():
        return 1

    def linear(n):
        for _ in range(n):
            mark()

    def quadratic(n):
        for _ in range(n):
            for _ in range(n):
                mark()

    def halving(n):
        while n > 1:
            n //= 2
            mark()

    assert growth(linear, lambda n: n, 300, "mark") == 2.0
    assert growth(quadratic, lambda n: n, 30, "mark") == 4.0
    assert growth(halving, lambda n: n, 1024, "mark") == 11 / 10
