import csv


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


def read_rows(path):
    """Return the rows as dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def amount_of(row):
    """Return the row's amount as a number."""
    return float(row["amount"])


def good_rows(rows):
    """Return the rows whose amount is a number."""
    good = []
    for row in rows:
        if amount_of(row) is not None:
            good.append(row)
    return good


def totals_by_region(rows):
    """Return region -> total."""
    totals = {}
    for row in good_rows(rows):
        totals[row["region"]] = totals.get(row["region"], 0) + amount_of(row)
    return totals


def report_lines(rows):
    """Return the report lines."""
    totals = totals_by_region(rows)
    lines = []
    total = 0
    for region in totals:
        lines.append(f"{region}: {totals[region]:.2f}")
        total += totals[region]
    lines.append(f"Rows: {len(rows)}")
    lines.append(f"Bad rows: {len(rows) - len(good_rows(rows))}")
    lines.append(f"Total: {total:.2f}")
    return lines


def write_report(path, lines):
    """Write the lines to the file."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def test_report():
    rows = [{"date": "d", "region": "a", "amount": "1.5"}, {"date": "d", "region": "b", "amount": "2"}]
    assert amount_of(rows[0]) == 1.5
    assert good_rows(rows) == rows
    assert totals_by_region(rows) == {"a": 1.5, "b": 2.0}
    assert report_lines(rows) == ["a: 1.50", "b: 2.00", "Rows: 2", "Bad rows: 0", "Total: 3.50"]
    print("report: all checks passed")


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
