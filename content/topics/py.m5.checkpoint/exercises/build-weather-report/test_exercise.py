from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def sample():
    return [
        {"name": "Lima", "temps": [18, 20, 19]},
        {"name": "Cairo", "temps": [30, 33, 29]},
        {"name": "Oslo", "temps": [4, 7, 5]},
    ]


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_average():
    """average([30, 33, 29]) is about 30.67, and average([5]) is 5.0."""
    average = function("average")
    assert abs(average([30, 33, 29]) - 30.6667) < 0.001
    assert average([5]) == 5.0


def test_label():
    """label: hot at 25, mild at 24.9 and 15, cold at 14.9."""
    label = function("label")
    assert label(25) == "hot"
    assert label(40) == "hot"
    assert label(24.9) == "mild"
    assert label(15) == "mild"
    assert label(14.9) == "cold"
    assert label(-5) == "cold"


def test_hottest():
    """hottest picks the highest average, the first of two who tie."""
    hottest = function("hottest")
    assert hottest(sample()) == "Cairo"
    tie = [{"name": "X", "temps": [20]}, {"name": "Y", "temps": [20]}]
    assert hottest(tie) == "X"


def test_report_lines():
    """report_lines gives one formatted line per city, then the Hottest line."""
    report_lines = function("report_lines")
    assert report_lines(sample()) == [
        "Lima: 19.0 (mild)",
        "Cairo: 30.7 (hot)",
        "Oslo: 5.3 (cold)",
        "Hottest: Cairo",
    ]
    assert report_lines([{"name": "Rome", "temps": [25]}]) == ["Rome: 25.0 (hot)", "Hottest: Rome"]


def test_leaves_data_alone():
    """No function changes the cities list or any temps list."""
    cities = sample()
    function("report_lines")(cities)
    function("hottest")(cities)
    function("average")(cities[0]["temps"])
    assert cities == sample()


def test_docstrings():
    """Every function has a docstring."""
    for name in ("average", "label", "hottest", "report_lines", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_weather has 4 or more asserts, passes, and fails when label always says hot."""
    assert count_asserts() >= 4
    test = function("test_weather")
    test()
    import solution

    original = solution.label
    solution.label = lambda average: "hot"
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.label = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report."""
    assert run() == (
        "weather: all checks passed\nLima: 19.0 (mild)\nCairo: 30.7 (hot)\nOslo: 5.3 (cold)\n"
        "Hottest: Cairo\n"
    )
