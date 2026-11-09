import csv


def rows_where(path, field, value):
    """Return the rows of the CSV file whose field equals value."""
    matches = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row[field] == value:
                matches.append(row[field])
    return matches
