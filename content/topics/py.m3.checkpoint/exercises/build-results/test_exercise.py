import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def stats(results):
    """The three statistics the program printed, whatever the format:
    (7, 5, 3). Missing parts come back as None."""
    printed = run(results + "\n")
    games = re.search(r"Games:\s*(\d+)", printed)
    wins = re.search(r"Wins:\s*(\d+)", printed)
    longest = re.search(r"Longest winning streak:\s*(\d+)", printed)
    return (
        int(games.group(1)) if games else None,
        int(wins.group(1)) if wins else None,
        int(longest.group(1)) if longest else None,
    )


def bars(results):
    """The lines of the chart: every printed line made only of #."""
    printed = run(results + "\n")
    return [line for line in printed.splitlines() if line and set(line) == {"#"}]


def test_games():
    """Counts the games: 7 in WWLWWWL, 1 in W."""
    assert stats("WWLWWWL")[0] == 7
    assert stats("W")[0] == 1


def test_wins():
    """Counts the wins: 5 in WWLWWWL, 0 in LL."""
    assert stats("WWLWWWL")[1] == 5
    assert stats("LL")[1] == 0
    assert stats("WLW")[1] == 2


def test_streak():
    """Finds the longest streak: 3 in WWLWWWL, 1 in WLWLW, 0 in LL."""
    assert stats("WWLWWWL")[2] == 3
    assert stats("WLWLW")[2] == 1
    assert stats("LL")[2] == 0


def test_last_streak():
    """A streak at the very end counts too: LWWWW has a longest streak of 4."""
    assert stats("LWWWW")[2] == 4
    assert stats("WLWW")[2] == 2


def test_chart():
    """Draws one bar per winning streak, with one # per win, and nothing for a team with no wins."""
    assert bars("WWLWWWL") == ["##", "###"]
    assert bars("WLLW") == ["#", "#"]
    assert bars("LL") == []


def test_layout():
    """Prints exactly the three statistics lines and then the bars, as in the example."""
    assert run("WWLWWWL\n") == "Games: 7\nWins: 5\nLongest winning streak: 3\n##\n###\n"
