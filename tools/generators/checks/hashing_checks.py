# Throwaway checks for the hashing topic's recall items and Tracked budgets.
print("409600/1414 =", 409600 / 1414)
names = [f"user{i}" for i in range(1000)]
from collections import Counter
print("name lengths:", Counter(len(n) for n in names))
# bad-hash per-lookup average given bucket order preserved
print("bad hash expected:", 900*450.5 + 90*45.5 + 10*5.5)

def tiny_hash(key):
    return sum(ord(ch) for ch in key)
for key in ("cat", "act", "dog"):
    print("bucket-index:", key, tiny_hash(key), tiny_hash(key) % 8)

def insert_at_front(items, value):
    items.append(None)
    moves = 0
    for i in range(len(items) - 1, 0, -1):
        items[i] = items[i - 1]
        moves += 1
    items[0] = value
    return moves
items = [10, 20, 30]
print("list-shift:", insert_at_front(items, 5), items)
print("list-shift:", insert_at_front(items, 1), items)

words = ["a", "b", "a", "c", "a"]
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
print("parsons-count-words:", counts["a"], len(counts))

class Tracked:
    compared = 0
    def __init__(self, value): self.value = value
    def __hash__(self): return hash(self.value)
    def __eq__(self, other):
        Tracked.compared += 1
        return self.value == other.value
    def __lt__(self, other):
        Tracked.compared += 1
        return self.value < other.value
def tracked(values): return [Tracked(v) for v in values]

def count_frequencies(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts
def count_scans(items):
    counts = {}
    for item in items:
        counts[item] = items.count(item)
    return counts
Tracked.compared = 0; count_frequencies(tracked([i % 100 for i in range(3000)])); print("count_frequencies dict:", Tracked.compared)
Tracked.compared = 0; count_scans(tracked([i % 100 for i in range(3000)])); print("count_frequencies items.count:", Tracked.compared)

def group_by(records, field):
    groups = {}
    for record in records:
        groups.setdefault(record[field], []).append(record)
    return groups
def join_index(left, right, field):
    by_key = group_by(right, field)
    merged = []
    for record in left:
        for match in by_key.get(record[field], []):
            merged.append({**record, **match})
    return merged
def join_scan(left, right, field):
    merged = []
    for record in left:
        for match in right:
            if match[field] == record[field]:
                merged.append({**record, **match})
    return merged
for name, fn in (("index", join_index), ("scan", join_scan)):
    left = [{"id": key} for key in tracked(range(1000))]
    right = [{"id": key, "n": i} for i, key in enumerate(tracked([i % 1000 for i in range(2000)]))]
    Tracked.compared = 0
    rows = fn(left, right, "id")
    print("join", name, ":", len(rows), "rows,", Tracked.compared, "comparisons; left records:", len(left))
