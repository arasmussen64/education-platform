import bisect
import random

import numpy as np


def binary_search(items, target, counter):
    """The index of target in a sorted list, or -1: look in the middle, keep the half that can hold it."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        counter[0] += 1
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def scan(items, target, counter):
    for i, item in enumerate(items):
        counter[0] += 1
        if item == target:
            return i
    return -1


evens = list(range(0, 2_000_000, 2))
for name, search in (("scan", scan), ("binary search", binary_search)):
    counter = [0]
    found = search(evens, 1_999_998, counter)
    missing = search(evens, 1_999_999, counter)
    print(name + ": found at", found, "and missing is", missing, "after", counter[0], "comparisons")


def insertion_sort(items, counter):
    """Grow a sorted front: each item shifts left past the larger ones and stops."""
    result = list(items)
    for i in range(1, len(result)):
        value = result[i]
        j = i - 1
        while j >= 0:
            counter[0] += 1
            if result[j] <= value:
                break
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = value
    return result


def merge_sort(items, counter):
    """Split in half, sort each half the same way, merge the two sorted halves."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], counter)
    right = merge_sort(items[middle:], counter)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


for n in (1000, 2000):
    data = list(range(n))
    random.Random(1).shuffle(data)
    counts = {}
    for name, sort in (("insertion", insertion_sort), ("merge", merge_sort)):
        counter = [0]
        assert sort(data, counter) == list(range(n))
        counts[name] = counter[0]
    print(n, "shuffled items:", counts)
counter = [0]
insertion_sort(list(range(2000)), counter)
print("2000 already sorted items: insertion", counter[0])

records = [("Oslo", 30), ("Lima", 12), ("Oslo", 8), ("Pune", 19), ("Lima", 41)]
print(sorted(records, key=lambda record: record[0]))
print(sorted(records, key=lambda record: (record[0], -record[1])))

bands = [50, 65, 80, 90]
for score in (49, 65, 79, 95):
    print(score, "is in band", bisect.bisect_right(bands, score))

names = np.array(["ann", "bob", "cy", "dee"])
scores = np.array([71, 93, 58, 93])
order = np.argsort(-scores, kind="stable")
print(order, names[order])
