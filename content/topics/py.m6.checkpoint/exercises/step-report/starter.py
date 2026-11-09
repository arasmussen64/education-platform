import csv


# The sample file
def write_sample(path):
    """Write the sample sales file."""
    with open(path, "w") as f:
        f.write("date,region,amount\n")
        f.write("2026-01-03,north,120.50\n")
        f.write("2026-01-03,south,80\n")
        f.write("2026-01-04,north,abc\n")
        f.write("2026-01-04,east,45.25\n")
        f.write("2026-01-05,south,\n")
        f.write("2026-01-05,north,30\n")


# Reading, and deciding which rows are good
def read_rows(path):
    """Return the rows of a CSV file as a list of dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def amount_of(row):
    """Return the row's amount as a number, or None when it's blank or not a number."""
    try:
        return float(row["amount"])
    except ValueError:
        return None


def good_rows(rows):
    """Return the rows whose amount is a number, in order."""
    good = []
    for row in rows:
        if amount_of(row) is not None:
            good.append(row)
    return good


# Totals by region
def totals_by_region(rows):
    """Return a dictionary of region to total amount, over the good rows."""
    totals = {}
    for row in good_rows(rows):
        region = row["region"]
        totals[region] = totals.get(region, 0) + amount_of(row)
    return totals


# The report as lines, and writing it
def report_lines(rows):
    """Return a line per region, then Rows, Bad rows and Total."""
    totals = totals_by_region(rows)
    lines = []
    total = 0
    for region in totals:
        lines.append(f"{region}: {totals[region]:...}")
        total += totals[region]
    lines.append(f"Rows: {len(rows)}")
    lines.append(f"Bad rows: {len(rows) - ...}")
    lines.append(f"Total: {total:.2f}")
    return lines


def write_report(path, lines):
    """Write the lines to the file, one per line, replacing what was there."""
    with open(path, ...) as f:
        for line in lines:
            f.write(line + ...)


# The tests
def test_report():
    rows = [
        {"date": "d", "region": "a", "amount": "1.5"},
        {"date": "d", "region": "b", "amount": "abc"},
        {"date": "d", "region": "a", "amount": ""},
        {"date": "d", "region": "b", "amount": "2"},
    ]
    assert amount_of(rows[0]) == 1.5
    assert amount_of(rows[1]) is None
    assert amount_of(rows[2]) is None
    assert good_rows(rows) == [rows[0], rows[3]]
    assert totals_by_region(rows) == {"a": 1.5, "b": 2.0}
    assert report_lines(rows) == [
        "a: 1.50",
        "b: 2.00",
        "Rows: 4",
        "Bad rows: 2",
        "Total: 3.50",
    ]
    print("report: all checks passed")


# The program
def main():
    """Write the sample, read it, write the report and print it."""
    write_sample("sales.csv")
    rows = read_rows("sales.csv")
    lines = report_lines(rows)
    write_report("report.txt", lines)
    for line in lines:
        print(line)


if __name__ == "__main__":
    test_report()
    main()
