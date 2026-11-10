def fib(n):
    """The n-th Fibonacci number, smallest cases first, with no recursion."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def edit_distance(a, b):
    """The fewest single-character inserts, deletes and substitutions turning a into b."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + 1)
    return table[len(a)][len(b)]


def knapsack(items, capacity):
    """(best value, names chosen in the given order) for items of (name, weight, value) that fit the capacity."""
    best = [[0] * (capacity + 1) for _ in range(len(items) + 1)]
    for i, (name, weight, value) in enumerate(items, start=1):
        for room in range(capacity + 1):
            best[i][room] = best[i - 1][room]
            if weight <= room:
                best[i][room] = max(best[i][room], best[i - 1][room - weight] + value)
    chosen = []
    room = capacity
    for i in range(len(items), 0, -1):
        if best[i][room] != best[i - 1][room]:
            chosen.append(items[i - 1][0])
            room -= items[i - 1][1]
    return best[len(items)][capacity], chosen[::-1]


def min_coins(coins, amount):
    """The fewest coins that make the amount, or -1 if none can."""
    best = [0] + [float("inf")] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] + 1 < best[total]:
                best[total] = best[total - coin] + 1
    return best[amount] if best[amount] != float("inf") else -1


print(fib(10), fib(90))
print(edit_distance("kitten", "sitting"), edit_distance("", "abc"), edit_distance("flaw", "lawn"))
gear = [("tent", 5, 60), ("stove", 3, 50), ("water", 4, 70), ("book", 2, 30)]
print(knapsack(gear, 9))
print(min_coins([1, 5, 10, 25], 63), min_coins([1, 15, 25], 30), min_coins([4, 7], 10))
