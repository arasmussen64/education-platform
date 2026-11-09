CITIES = [
    {"name": "Lima", "temps": [18, 20, 19]},
    {"name": "Cairo", "temps": [30, 33, 29]},
    {"name": "Oslo", "temps": [4, 7, 5]},
]


def average(temps):
    """Return the average of a non-empty list of temperatures."""
    total = 0
    for temp in temps:
        total += temp
    return total / len(temps)


def label(average):
    """Return hot for 25 or more, mild for 15 or more, otherwise cold."""
    if average >= 25:
        return "hot"
    if average >= 15:
        return "mild"
    return "cold"


def hottest(cities):
    """Return the name of the city with the highest average, the first if two tie."""
    best = cities[0]
    for city in cities:
        if average(city["temps"]) > average(best["temps"]):
            best = city
    return best["name"]


def report_lines(cities):
    """Return one line per city, like 'Lima: 19.0 (mild)', then 'Hottest: Cairo'."""
    lines = []
    for city in cities:
        avg = average(city["temps"])
        lines.append(f"{city['name']}: {avg:.1f} ({label(avg)})")
    lines.append(f"Hottest: {hottest(cities)}")
    return lines


def test_weather():
    assert average([10, 20]) == 15.0
    assert label(25) == "hot"
    assert label(24.9) == "mild"
    assert label(15) == "mild"
    assert label(14.9) == "cold"
    assert hottest(CITIES) == "Cairo"
    print("weather: all checks passed")


def main():
    """Print the report."""
    for line in report_lines(CITIES):
        print(line)


if __name__ == "__main__":
    test_weather()
    main()
