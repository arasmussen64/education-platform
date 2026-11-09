def column_values(path, field):
    """Return the values of one column of a CSV file, in order."""
    values = []
    with open(path) as f:
        for line in f:
            values.append(line.rstrip().split(",")[1])
    return values
