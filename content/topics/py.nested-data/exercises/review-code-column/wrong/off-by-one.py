def column(grid, index):
    """Return the values in one column of the grid, top to bottom."""
    values = []
    for row in grid:
        values.append(row[index - 1])
    return values
