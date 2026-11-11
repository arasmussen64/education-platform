# Throwaway checks for the sorting topic's recall items, look counts and Tracked budgets.
import bisect, math, random
import numpy as np

items = [2, 3, 5, 7, 11, 13, 17, 19]
def looks(items, target):
    lo, hi = 0, len(items) - 1
    n = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        n += 1
        if items[mid] == target:
            return n, mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return n, -1
print("predict-a-binary-search looks for 13:", looks(items, 13))
print("max looks over 8 items (present):", max(looks(items, t)[0] for t in items), "; for missing 20:", looks(items, 20), "; for 1:", looks(items, 1))
big = list(range(0, 2_000_000, 2))
print("million items: find last", looks(big, 1_999_998)[0], "missing", looks(big, 1_999_999)[0], "find first", looks(big, 0)[0], "max over sample:", max(looks(big, t)[0] for t in range(0, 2_000_000, 20002)))
print("log2(2e6) =", math.log2(2_000_000), "2e6*log2 =", 2_000_000 * math.log2(2_000_000), "50_000*21 =", 50_000 * 21)
print("log2(1e6) =", math.log2(1_000_000), "1e6*20 =", 1_000_000 * 20, "(1e6)^2/4 =", 1_000_000**2 / 4)
print("50_000 * 2_000_000 =", 50_000 * 2_000_000)
print("insertion n^2/4 at 3000:", 3000**2 / 4, "merge n log2 n at 3000:", 3000 * math.log2(3000))

records = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]
print("stable:", [name for name, score in sorted(records, key=lambda r: r[1])])
print("stable reverse:", [name for name, score in sorted(records, key=lambda r: r[1], reverse=True)])

grades = [60, 70, 80, 90]
print("bisect:", [(s, bisect.bisect_right(grades, s)) for s in (59, 60, 85, 100)])

recs = [("ann", 3), ("bob", 1), ("cy", 2)]
print("parsons by score:", [n for n, s in sorted(recs, key=lambda r: r[1])], "decoy:", [n for n, s in sorted(recs, key=lambda r: r[0])])

scores = np.array([71, 93, 58]); names = np.array(["ann", "bob", "cy"])
print("argsort:", np.argsort(scores), names[np.argsort(scores)])

class Tracked:
    compared = 0
    def __init__(self, value): self.value = value
    def _count(self): Tracked.compared += 1
    def __eq__(self, other): self._count(); return self.value == other.value
    def __lt__(self, other): self._count(); return self.value < other.value
    def __le__(self, other): self._count(); return self.value <= other.value
    def __gt__(self, other): self._count(); return self.value > other.value
    def __ge__(self, other): self._count(); return self.value >= other.value
    def __hash__(self): return hash(self.value)
def tracked(values): return [Tracked(v) for v in values]

def binary_search(items, target):
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target: return mid
        if items[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
items = tracked(range(0, 200_000, 2)); Tracked.compared = 0
binary_search(items, Tracked(199_998)); binary_search(items, Tracked(199_999))
print("binary search Tracked comparisons, two searches on 100k:", Tracked.compared)

def insertion_sort(items):
    result = list(items)
    for i in range(1, len(result)):
        value = result[i]; j = i - 1
        while j >= 0 and result[j] > value:
            result[j + 1] = result[j]; j -= 1
        result[j + 1] = value
    return result
def insertion_from_left(items):
    result = []
    for value in items:
        position = 0
        while position < len(result) and result[position] <= value:
            position += 1
        result.insert(position, value)
    return result
def merge_sort(items):
    if len(items) <= 1: return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle]); right = merge_sort(items[middle:])
    merged = []; i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: merged.append(left[i]); i += 1
        else: merged.append(right[j]); j += 1
    merged.extend(left[i:]); merged.extend(right[j:])
    return merged
Tracked.compared = 0; insertion_sort(tracked(range(3000))); print("insertion sorted 3000:", Tracked.compared)
Tracked.compared = 0; insertion_from_left(tracked(range(3000))); print("insertion-from-left sorted 3000:", Tracked.compared)
data = list(range(3000)); random.Random(4).shuffle(data)
Tracked.compared = 0; merge_sort(tracked(data)); print("merge shuffled 3000 (seed 4):", Tracked.compared)
Tracked.compared = 0; insertion_sort(tracked(data)); print("insertion shuffled 3000 (seed 4):", Tracked.compared)
# merge of two 500-lists
def merge_count(left, right):
    i = j = 0; c = 0
    while i < len(left) and j < len(right):
        c += 1
        if left[i] <= right[j]: i += 1
        else: j += 1
    return c
print("merge 500+500 interleaved:", merge_count(list(range(0,1000,2)), list(range(1,1000,2))), "disjoint:", merge_count(list(range(500)), list(range(500,1000))))
