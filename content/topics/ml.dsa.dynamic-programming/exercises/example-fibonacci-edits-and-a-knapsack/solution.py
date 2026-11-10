from functools import lru_cache

calls = 0


def fib_plain(n):
    """The definition as a function: two calls per call, most of them repeats."""
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)


print("fib_plain(25) =", fib_plain(25), "after", calls, "calls")

memo = {}


def fib_memo(n):
    """The same, remembering every answer in a dict."""
    global calls
    calls += 1
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1) + fib_memo(n - 2)
    return memo[n]


calls = 0
print("fib_memo(25) =", fib_memo(25), "after", calls, "calls")


@lru_cache(maxsize=None)
def fib_cached(n):
    """The same, with the standard library remembering for you."""
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


print("fib_cached(25) =", fib_cached(25), fib_cached.cache_info())


def fib_bottom_up(n):
    """Smallest cases first, keeping only the last two: no recursion at all."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


print("fib_bottom_up(90) =", fib_bottom_up(90))


def edit_distance(a, b):
    """The fewest single-character edits (insert, delete, substitute) turning a into b, with the table."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)
    return table[len(a)][len(b)], table


def edits(a, b, table):
    """Walk the table back from the corner to list the edits that were counted."""
    i, j = len(a), len(b)
    steps = []
    while i > 0 or j > 0:
        cost = 0 if i > 0 and j > 0 and a[i - 1] == b[j - 1] else 1
        if i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + cost:
            if cost:
                steps.append(f"substitute {a[i - 1]} with {b[j - 1]}")
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            steps.append(f"delete {a[i - 1]}")
            i -= 1
        else:
            steps.append(f"insert {b[j - 1]}")
            j -= 1
    return steps[::-1]


distance, table = edit_distance("kitten", "sitting")
print("kitten -> sitting:", distance, "edits")
for row in table:
    print(" ".join(f"{cell:2}" for cell in row))
print(edits("kitten", "sitting", table))


def knapsack(items, capacity):
    """The most valuable set of items that fits: a table of the best value by items considered and room left."""
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
            name, weight, value = items[i - 1]
            chosen.append(name)
            room -= weight
    return best[len(items)][capacity], chosen[::-1]


gear = [("tent", 5, 60), ("stove", 3, 50), ("water", 4, 70), ("book", 2, 30)]
print("knapsack of 9:", knapsack(gear, 9))
greedy, room = [], 9
for name, weight, value in sorted(gear, key=lambda item: -item[2]):
    if weight <= room:
        greedy.append(name)
        room -= weight
print("greedy by value:", greedy, "worth", sum(value for name, weight, value in gear if name in greedy))
