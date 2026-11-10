def binary_search(items, target):
    """The index of target in a sorted list, or -1."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


readings = [41, 7, 19, 73, 2, 56, 30, 88, 64, 11]
ordered = sorted(readings)
print(ordered)
for target in (2, 30, 88, 50):
    print(target, "at index", binary_search(ordered, target))
