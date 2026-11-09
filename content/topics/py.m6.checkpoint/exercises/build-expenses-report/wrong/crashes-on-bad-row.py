import csv


def write_sample(path):
    """Write the sample expenses file."""
    with open(path, "w") as f:
        f.write("date,category,cost\n")
        f.write("2026-02-01,food,12.20\n")
        f.write("2026-02-01,travel,40\n")
        f.write("2026-02-02,food,abc\n")
        f.write("2026-02-02,food,49.50\n")
        f.write("2026-02-03,rent,\n")
        f.write("2026-02-03,travel,15.75\n")


def read_rows(path):
    """Return the rows as dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def cost_of(row):
    """Return the row's cost as a number."""
    return float(row["cost"])


def good_rows(rows):
    """Return the rows whose cost is a number."""
    good = []
    for row in rows:
        if cost_of(row) is not None:
            good.append(row)
    return good


def totals_by_category(rows):
    """Return category -> total."""
    totals = {}
    for row in good_rows(rows):
        totals[row["category"]] = totals.get(row["category"], 0) + cost_of(row)
    return totals


def report_lines(rows):
    """Return the report lines."""
    totals = totals_by_category(rows)
    lines = []
    total = 0
    for category in totals:
        lines.append(f"{category}: {totals[category]:.2f}")
        total += totals[category]
    lines.append(f"Rows: {len(rows)}")
    lines.append(f"Bad rows: {len(rows) - len(good_rows(rows))}")
    lines.append(f"Total: {total:.2f}")
    return lines


def write_report(path, lines):
    """Write the lines to the file."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def test_expenses():
    rows = [{"date": "d", "category": "a", "cost": "1.5"}, {"date": "d", "category": "b", "cost": "2"}]
    assert cost_of(rows[0]) == 1.5
    assert good_rows(rows) == rows
    assert totals_by_category(rows) == {"a": 1.5, "b": 2.0}
    assert report_lines(rows) == ["a: 1.50", "b: 2.00", "Rows: 2", "Bad rows: 0", "Total: 3.50"]
    print("expenses: all checks passed")


def main():
    """Write the sample, read it, write the report and print it."""
    write_sample("expenses.csv")
    rows = read_rows("expenses.csv")
    lines = report_lines(rows)
    write_report("expenses.txt", lines)
    for line in lines:
        print(line)


if __name__ == "__main__":
    test_expenses()
    main()
