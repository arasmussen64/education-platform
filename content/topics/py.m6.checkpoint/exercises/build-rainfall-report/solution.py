import csv


def write_sample(path):
    """Write the sample rainfall file."""
    with open(path, "w") as f:
        f.write("day,station,mm\n")
        f.write("1,hill,4.5\n")
        f.write("1,valley,2.0\n")
        f.write("2,hill,n/a\n")
        f.write("2,valley,5.5\n")
        f.write("3,hill,8.0\n")


def read_rows(path):
    """Return the rows of a CSV file as a list of dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def mm_of(row):
    """Return the row's reading as a number, or None when it's blank or not a number."""
    try:
        return float(row["mm"])
    except ValueError:
        return None


def good_rows(rows):
    """Return the rows whose reading is a number, in order."""
    good = []
    for row in rows:
        if mm_of(row) is not None:
            good.append(row)
    return good


def totals_by_station(rows):
    """Return a dictionary of station to total millimetres, over the good rows."""
    totals = {}
    for row in good_rows(rows):
        station = row["station"]
        totals[station] = totals.get(station, 0) + mm_of(row)
    return totals


def report_lines(rows):
    """Return a line per station, then Rows, Bad rows and Total."""
    totals = totals_by_station(rows)
    lines = []
    total = 0
    for station in totals:
        lines.append(f"{station}: {totals[station]:.1f}")
        total += totals[station]
    lines.append(f"Rows: {len(rows)}")
    lines.append(f"Bad rows: {len(rows) - len(good_rows(rows))}")
    lines.append(f"Total: {total:.1f}")
    return lines


def write_report(path, lines):
    """Write the lines to the file, one per line, replacing what was there."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def test_rainfall():
    rows = [
        {"day": "1", "station": "a", "mm": "1.5"},
        {"day": "1", "station": "b", "mm": "n/a"},
        {"day": "2", "station": "a", "mm": ""},
        {"day": "2", "station": "b", "mm": "2"},
    ]
    assert mm_of(rows[0]) == 1.5
    assert mm_of(rows[1]) is None
    assert mm_of(rows[2]) is None
    assert good_rows(rows) == [rows[0], rows[3]]
    assert totals_by_station(rows) == {"a": 1.5, "b": 2.0}
    assert report_lines(rows) == ["a: 1.5", "b: 2.0", "Rows: 4", "Bad rows: 2", "Total: 3.5"]
    print("rainfall: all checks passed")


def main():
    """Write the sample, read it, write the report and print it."""
    write_sample("rainfall.csv")
    rows = read_rows("rainfall.csv")
    lines = report_lines(rows)
    write_report("rainfall.txt", lines)
    for line in lines:
        print(line)


if __name__ == "__main__":
    test_rainfall()
    main()
