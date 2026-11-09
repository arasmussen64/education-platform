def count_lines(path):
    """Return how many lines the file has."""
    count = 0
    with open(path) as f:
        for line in path:
            count += 1
    return count
