def pairs(n):
    """How many pairs a nested loop over n items compares: n * (n - 1) / 2."""
    return n * n // 2


def has_duplicate(items):
    """Does any value appear twice? One pass with a set."""
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False


def common_count(a, b):
    """How many distinct values appear in both lists."""
    in_a = set(a)
    return len({item for item in b if item in in_a})


def growth_name(counts):
    """Name the growth from step counts at n, 2n, 4n, ...: the average ratio between neighbours."""
    ratios = [later / earlier for earlier, later in zip(counts, counts[1:])]
    average = sum(ratios) / len(ratios)
    if average < 1.5:
        return "constant"
    if average < 3:
        return "linear"
    if average < 6:
        return "quadratic"
    return "faster than quadratic"


print(pairs(10), pairs(1000))
print(has_duplicate([3, 1, 4, 1, 5]), has_duplicate(list(range(10000))))
print(common_count(["a", "b", "c"], ["b", "c", "d"]), common_count(list(range(5000)), list(range(2500, 7500))))
print(growth_name([pairs(100), pairs(200), pairs(400)]), growth_name([100, 200, 400]))
