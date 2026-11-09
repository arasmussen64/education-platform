import csv


def read_rows(path):
    """Return the rows as dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def total_of(rows, field):
    """Return the total of a field."""
    total = 0
    for row in rows:
        total += row[field]
    return total


def count_by(rows, field):
    """Return a count per value."""
    counts = {}
    for row in rows:
        counts[row[field]] = counts.get(row[field], 0) + 1
    return counts


def write_sample(path):
    """Write the sample file."""
    with open(path, "w") as f:
        f.write("item,region,amount\npen,north,2.5\nbook,south,10\nlamp,north,150\nmug,south,8\n")


def main():
    write_sample("sales.csv")
    rows = read_rows("sales.csv")
    print(f"Rows: {len(rows)}")
    print(f"Total amount: {total_of(rows, 'amount')}")
    print(f"By region: {count_by(rows, 'region')}")


if __name__ == "__main__":
    main()
