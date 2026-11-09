import csv


def column_values(path, field):
    """Return the values of one column of a CSV file, in order."""
    values = []
    with open(path) as f:
        for row in csv.DictReader(f):
            values.append(row[field])
    return values
