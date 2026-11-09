from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def sample():
    return [
        {"name": "Ada", "points": [22, 18, 27]},
        {"name": "Bob", "points": [8, 12, 10]},
        {"name": "Cy", "points": [15, 20, 13]},
    ]


def count_asserts():
    source = Path("solution.py").read_text(encoding="utf-8")
    return sum(1 for line in source.splitlines() if line.strip().startswith("assert "))


def test_average():
    """average([22, 18, 27]) is about 22.33, and average([10]) is 10.0."""
    average = function("average")
    assert abs(average([22, 18, 27]) - 22.3333) < 0.001
    assert average([10]) == 10.0


def test_rating():
    """rating: star at 20, starter at 19.9 and 10, bench at 9.9."""
    rating = function("rating")
    assert rating(20) == "star"
    assert rating(25) == "star"
    assert rating(19.9) == "starter"
    assert rating(10) == "starter"
    assert rating(9.9) == "bench"
    assert rating(0) == "bench"


def test_top_scorer():
    """top_scorer picks the highest average, the first of two who tie."""
    top_scorer = function("top_scorer")
    assert top_scorer(sample()) == "Ada"
    tie = [{"name": "X", "points": [12]}, {"name": "Y", "points": [12]}]
    assert top_scorer(tie) == "X"


def test_report_lines():
    """report_lines gives one formatted line per player, then the Top scorer line."""
    report_lines = function("report_lines")
    assert report_lines(sample()) == [
        "Ada: 22.3 (star)",
        "Bob: 10.0 (starter)",
        "Cy: 16.0 (starter)",
        "Top scorer: Ada",
    ]
    assert report_lines([{"name": "Dee", "points": [4]}]) == ["Dee: 4.0 (bench)", "Top scorer: Dee"]


def test_leaves_data_alone():
    """No function changes the players list or any points list."""
    players = sample()
    function("report_lines")(players)
    function("top_scorer")(players)
    function("average")(players[0]["points"])
    assert players == sample()


def test_docstrings():
    """Every function has a docstring."""
    for name in ("average", "rating", "top_scorer", "report_lines", "main"):
        assert (function(name).__doc__ or "").strip() != "", name


def test_tests():
    """test_team has 4 or more asserts, passes, and fails when rating always says star."""
    assert count_asserts() >= 4
    test = function("test_team")
    test()
    import solution

    original = solution.rating
    solution.rating = lambda average: "star"
    caught = False
    try:
        test()
    except AssertionError:
        caught = True
    finally:
        solution.rating = original
    assert caught


def test_program():
    """Run directly, the file prints the tests' message and the report."""
    assert run() == (
        "team: all checks passed\nAda: 22.3 (star)\nBob: 10.0 (starter)\nCy: 16.0 (starter)\n"
        "Top scorer: Ada\n"
    )
