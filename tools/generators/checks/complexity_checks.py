# Throwaway checks for the complexity topic's recall items and Tracked budgets.
def pairs(n):
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            count += 1
    return count
print("predict-count-the-pairs:", pairs(10), pairs(20), pairs(40), round(pairs(40) / pairs(20), 2))

def steps(n):
    return 3 * n * n + 100 * n
for n in (10, 100, 1000):
    print("doubling-counts:", n, steps(n), round(steps(2 * n) / steps(n), 2))

def halvings(n):
    s = 0
    while n > 1:
        n = n // 2
        s += 1
    return s
print("halving-steps:", halvings(16), halvings(1024), halvings(1_000_000))
import math
print("log2(1e6) =", math.log2(1_000_000))

# Parsons: count-the-nested-loop in order, and with the decoy
count = 0
n = 20
for i in range(n):
    for j in range(i + 1, n):
        count += 1
print("parsons honest:", count)
count = 0
for i in range(n):
    for j in range(n):
        count += 1
print("parsons decoy:", count)

class Tracked:
    compared = 0
    def __init__(self, value):
        self.value = value
    def __hash__(self):
        return hash(self.value)
    def __eq__(self, other):
        Tracked.compared += 1
        return self.value == other.value
    def __lt__(self, other):
        Tracked.compared += 1
        return self.value < other.value

def tracked(values):
    return [Tracked(v) for v in values]

# build: has_duplicate one-pass vs nested on 3000 distinct
def has_duplicate_set(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
def has_duplicate_nested(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False
Tracked.compared = 0; has_duplicate_set(tracked(range(3000))); print("has_duplicate set, 3000 distinct:", Tracked.compared)
Tracked.compared = 0; has_duplicate_nested(tracked(range(3000))); print("has_duplicate nested, 3000 distinct:", Tracked.compared)

def common_count_set(a, b):
    in_a = set(a)
    return len({item for item in b if item in in_a})
def common_count_nested(a, b):
    return len({item for item in b if item in a})
Tracked.compared = 0; r = common_count_set(tracked(range(3000)), tracked(range(2000, 5000))); print("common_count set:", r, Tracked.compared)
Tracked.compared = 0; r = common_count_nested(tracked(range(3000)), tracked(range(2000, 5000))); print("common_count nested:", r, Tracked.compared)

# debug: unique_in_order with list vs set on i % 1500 for 3000
def uio_list(emails):
    seen = []; result = []
    for e in emails:
        if e not in seen:
            seen.append(e); result.append(e)
    return result
def uio_set(emails):
    seen = set(); result = []
    for e in emails:
        if e not in seen:
            seen.add(e); result.append(e)
    return result
Tracked.compared = 0; uio_list(tracked([i % 1500 for i in range(3000)])); print("unique_in_order list:", Tracked.compared)
Tracked.compared = 0; uio_set(tracked([i % 1500 for i in range(3000)])); print("unique_in_order set:", Tracked.compared)
print("3000*2999/2 =", 3000*2999//2)
print("1000 s in minutes:", 1000/60, "1e6 s in days:", 1e6/86400)
