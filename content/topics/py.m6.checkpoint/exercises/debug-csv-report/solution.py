import csv


def write_sample(path):
    """Write a small sales file."""
    with open(path, "w") as f:
        f.write("date,region,amount\n")
        f.write("2026-01-03,north,120.50\n")
        f.write("2026-01-03,south,80\n")
        f.write("2026-01-04,north,abc\n")
        f.write("2026-01-05,north,30\n")


def read_rows(path):
    """Return the rows of a CSV file as a list of dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def amount_of(row):
    """Return the row's amount as a number, or None if it isn't one."""
    try:
        return float(row["amount"])
    except ValueError:
        return None


def totals_by_region(rows):
    """Return a dictionary of region to total amount, skipping bad rows."""
    totals = {}
    for row in rows:
        amount = amount_of(row)
        if amount is None:
            continue
        totals[row["region"]] = totals.get(row["region"], 0) + amount
    return totals


def report_lines(rows):
    """Return a line per region, then the row counts and the total."""
    totals = totals_by_region(rows)
    lines = []
    total = 0
    bad = 0
    for region in totals:
        lines.append(f"{region}: {totals[region]:.2f}")
        total += totals[region]
    for row in rows:
        if amount_of(row) is None:
            bad += 1
    lines.append(f"Rows: {len(rows)}")
    lines.append(f"Bad rows: {bad}")
    lines.append(f"Total: {total:.2f}")
    return lines


def write_report(path, lines):
    """Write the lines to the file, one per line."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def main():
    """Write the sample, read it, write the report and print it."""
    write_sample("sales.csv")
    rows = read_rows("sales.csv")
    lines = report_lines(rows)
    write_report("report.txt", lines)
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
