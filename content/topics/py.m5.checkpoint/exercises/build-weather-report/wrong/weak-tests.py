CITIES = [
    {"name": "Lima", "temps": [18, 20, 19]},
    {"name": "Cairo", "temps": [30, 33, 29]},
    {"name": "Oslo", "temps": [4, 7, 5]},
]


def average(temps):
    """Return the average."""
    total = 0
    for temp in temps:
        total += temp
    return total / len(temps)


def label(average):
    """Return the label."""
    if average >= 25:
        return "hot"
    if average >= 15:
        return "mild"
    return "cold"


def hottest(cities):
    """Return the hottest city's name."""
    best = cities[0]
    for city in cities:
        if average(city["temps"]) > average(best["temps"]):
            best = city
    return best["name"]


def report_lines(cities):
    """Return the report lines."""
    lines = []
    for city in cities:
        avg = average(city["temps"])
        lines.append(f"{city['name']}: {avg:.1f} ({label(avg)})")
    lines.append(f"Hottest: {hottest(cities)}")
    return lines


def test_weather():
    assert label(25) == "hot"
    assert label(30) == "hot"
    assert label(45) == "hot"
    assert hottest(CITIES) == "Cairo"
    print("weather: all checks passed")


def main():
    """Print the report."""
    for line in report_lines(CITIES):
        print(line)


if __name__ == "__main__":
    test_weather()
    main()
