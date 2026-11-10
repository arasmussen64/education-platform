memo = {}


def paths(rows, cols):
    """Ways to walk from the top-left of a grid to the bottom-right, moving only right or down."""
    if rows == 0 or cols == 0:
        return 0
    if (rows, cols) not in memo:
        memo[(rows, cols)] = paths(rows - 1, cols) + paths(rows, cols - 1)
    return memo[(rows, cols)]


print(paths(2, 2), paths(10, 10), paths(16, 16))
