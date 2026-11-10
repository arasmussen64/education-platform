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


primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
print(binary_search(primes, 2), binary_search(primes, 29), binary_search(primes, 13))
print(binary_search(primes, 4), binary_search([], 1))
