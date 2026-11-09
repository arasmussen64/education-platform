PLAYERS = [
    {"name": "Ada", "points": [22, 18, 27]},
    {"name": "Bob", "points": [8, 12, 10]},
    {"name": "Cy", "points": [15, 20, 13]},
]


def average(points):
    """Return the average of a non-empty list of points."""
    total = 0
    for value in points:
        total += value
    return total / len(points)


def rating(average):
    """Return star for 20 or more, starter for 10 or more, otherwise bench."""
    if average >= 20:
        return "star"
    if average >= 10:
        return "starter"
    return "bench"


def top_scorer(players):
    """Return the name of the player with the highest average, the first if two tie."""
    best = players[0]
    for player in players:
        if average(player["points"]) > average(best["points"]):
            best = player
    return best["name"]


def report_lines(players):
    """Return one line per player, like 'Ada: 22.3 (star)', then 'Top scorer: Ada'."""
    lines = []
    for player in players:
        avg = average(player["points"])
        lines.append(f"{player['name']}: {avg:.1f} ({rating(avg)})")
    lines.append(f"Top scorer: {top_scorer(players)}")
    return lines


def test_team():
    assert average([20, 10]) == 15.0
    assert rating(20) == "star"
    assert rating(19.9) == "starter"
    assert rating(10) == "starter"
    assert rating(9.9) == "bench"
    assert top_scorer(PLAYERS) == "Ada"
    print("team: all checks passed")


def main():
    """Print the report."""
    for line in report_lines(PLAYERS):
        print(line)


if __name__ == "__main__":
    test_team()
    main()
