import cProfile
import pstats

from checks import function, run


def test_the_output():
    """Prints the three counts."""
    printed = run()
    assert printed == '250 1 0\n', f"Your program printed:\n{printed}"


def test_another_profile():
    """Counts a function called 7 times, one called once, and one never called."""
    calls_to = function("calls_to")

    def seven():
        return 1

    def once():
        return sum(seven() for _ in range(7))

    profiler = cProfile.Profile()
    profiler.enable()
    once()
    profiler.disable()
    stats = pstats.Stats(profiler)
    assert calls_to(stats, "seven") == 7 and calls_to(stats, "once") == 1 and calls_to(stats, "never") == 0
