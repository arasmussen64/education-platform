import csv


def read_rows(path):
    """Return the rows of a CSV file as a list of dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def total_of(rows, field):
    """Return the total of a numeric field across the rows."""
    total = 0
    for row in rows:
        total += float(row[field])
    return total


def count_by(rows, field):
    """Return a dictionary of each value of the field to how many rows have it."""
    counts = {}
    for row in rows:
        counts[row[field]] = counts.get(row[field], 0) + 1
    return counts


def write_sample(path):
    """Write the sample sales file."""
    with open(path, "w") as f:
        f.write("item,region,amount\n")
        f.write("pen,north,2.5\n")
        f.write("book,south,10\n")
        f.write("lamp,north,150\n")
        f.write("mug,south,8\n")


def main():
    write_sample("sales.csv")
    rows = read_rows("sales.csv")
    print(f"Rows: {len(rows)}")
    print(f"Total amount: {total_of(rows, 'amount')}")
    print(f"By region: {count_by(rows, 'region')}")


if __name__ == "__main__":
    main()
