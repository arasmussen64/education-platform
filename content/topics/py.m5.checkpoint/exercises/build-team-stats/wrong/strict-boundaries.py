PLAYERS = [
    {"name": "Ada", "points": [22, 18, 27]},
    {"name": "Bob", "points": [8, 12, 10]},
    {"name": "Cy", "points": [15, 20, 13]},
]


def average(points):
    """Return the average."""
    total = 0
    for value in points:
        total += value
    return total / len(points)


def rating(average):
    """Return the rating."""
    if average > 20:
        return "star"
    if average > 10:
        return "starter"
    return "bench"


def top_scorer(players):
    """Return the top scorer's name."""
    best = players[0]
    for player in players:
        if average(player["points"]) > average(best["points"]):
            best = player
    return best["name"]


def report_lines(players):
    """Return the report lines."""
    lines = []
    for player in players:
        avg = average(player["points"])
        lines.append(f"{player['name']}: {avg:.1f} ({rating(avg)})")
    lines.append(f"Top scorer: {top_scorer(players)}")
    return lines


def test_team():
    assert rating(25) == "star"
    assert rating(15) == "starter"
    assert rating(5) == "bench"
    assert top_scorer(PLAYERS) == "Ada"
    print("team: all checks passed")


def main():
    """Print the report."""
    for line in report_lines(PLAYERS):
        print(line)


if __name__ == "__main__":
    test_team()
    main()
