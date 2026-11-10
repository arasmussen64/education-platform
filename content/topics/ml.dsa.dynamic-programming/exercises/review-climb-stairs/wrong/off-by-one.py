def ways(n):
    """Ways to climb n stairs taking 1 or 2 steps at a time, smallest cases first."""
    one_below, here = 1, 1
    for _ in range(n):
        one_below, here = here, one_below + here
    return here


print(ways(1), ways(2), ways(5), ways(30))
