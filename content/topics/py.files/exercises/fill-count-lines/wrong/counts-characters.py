def count_lines(path):
    """Return how many lines the file has."""
    count = 0
    with open(path) as f:
        for line in f:
            count += len(line)
    return count
