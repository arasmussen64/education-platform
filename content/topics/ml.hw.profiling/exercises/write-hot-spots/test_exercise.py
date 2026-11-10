import cProfile
import pstats

from checks import function, run


def test_the_output():
    """Prints the two hot spots in order."""
    printed = run()
    assert printed == "['heavy', 'light']\n", f"Your program printed:\n{printed}"


def test_another_profile():
    """A function that loops 50,000 times outranks one that loops 1,000 times, and the built-ins stay out of the list."""
    hot_spots = function("hot_spots")

    def alpha():
        total = 0
        for i in range(50_000):
            total += i
        return total

    def beta():
        total = 0
        for i in range(1_000):
            total += i
        return total

    def both():
        beta()
        return alpha()

    profiler = cProfile.Profile()
    profiler.enable()
    both()
    profiler.disable()
    stats = pstats.Stats(profiler)
    assert hot_spots(stats, 1) == ["alpha"] and hot_spots(stats, 2) == ["alpha", "beta"]
    assert all(not name.startswith("<") for name in hot_spots(stats, 10))
