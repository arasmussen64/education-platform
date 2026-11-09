def row_totals(grid):
    """Return a list with the total of each row."""
    totals = []
    for row in grid:
        total = 0
        for cell in row:
            total += cell
        totals.append(cell)
    return totals
