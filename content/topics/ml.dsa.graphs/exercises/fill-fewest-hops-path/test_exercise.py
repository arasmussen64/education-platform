from checks import function, run


def test_the_output():
    """Prints the three results."""
    printed = run()
    assert printed == "['A', 'B', 'D', 'F']\n['E', 'C', 'A', 'B']\nNone\n", f"Your program printed:\n{printed}"


def test_a_grid():
    """On a 20 by 20 grid, the path from one corner to the opposite one has 39 nodes."""
    fewest_hops_path = function("fewest_hops_path")
    grid = {}
    for r in range(20):
        for c in range(20):
            grid[(r, c)] = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < 20 and 0 <= c + dc < 20]
    path = fewest_hops_path(grid, (0, 0), (19, 19))
    assert len(path) == 39 and path[0] == (0, 0) and path[-1] == (19, 19)
