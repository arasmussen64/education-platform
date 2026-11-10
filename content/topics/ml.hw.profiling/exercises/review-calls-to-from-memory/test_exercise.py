import cProfile
import pstats

from checks import function, run


def test_the_output():
    """Prints the three counts."""
    assert run() == '250 1 0\n'


def test_another_profile():
    """Counts 7 calls, 1 call and 0 calls in a fresh profile."""
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
