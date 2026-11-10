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
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)
    return table[len(a)][len(b)]


def knapsack(items, capacity):
    """(best value, names chosen in the given order) for items of (name, weight, value) that fit the capacity."""
    chosen, room, total = [], capacity, 0
    for name, weight, value in sorted(items, key=lambda item: -item[2]):
        if weight <= room:
            chosen.append(name)
            room -= weight
            total += value
    return total, [name for name, weight, value in items if name in chosen]


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
