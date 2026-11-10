import cProfile
import pstats

from checks import function, run

EXPECTED = 'most own time: heavy | calls to light: 1000\n'


def test_the_output():
    """Names heavy as the hot spot and counts a thousand calls to light."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_functions_profile_as_described():
    """Under a fresh profile, run calls light a thousand times and heavy once, and heavy holds the most own time."""
    run_it = function("run")
    profiler = cProfile.Profile()
    profiler.enable()
    run_it()
    profiler.disable()
    rows = {func: row for (file, line, func), row in pstats.Stats(profiler).stats.items()}
    assert rows["light"][1] == 1000 and rows["heavy"][1] == 1 and rows["heavy"][2] > rows["light"][2]
