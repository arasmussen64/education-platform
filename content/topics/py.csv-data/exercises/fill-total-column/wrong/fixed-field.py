import csv


def total_of(path, field):
    """Return the total of a numeric column of a CSV file."""
    total = 0
    with open(path) as f:
        for row in csv.DictReader(f):
            total += float(row["amount"])
    return total
