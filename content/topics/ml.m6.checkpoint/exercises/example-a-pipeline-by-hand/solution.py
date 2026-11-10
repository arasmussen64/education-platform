import heapq
from collections import deque


def dedupe(records, key):
    """The first record for each value of the key field, in order: one pass with a set."""
    seen = set()
    kept = []
    for record in records:
        if record[key] not in seen:
            seen.add(record[key])
            kept.append(record)
    return kept


def top_k(records, field, k):
    """The k records with the largest field value, largest first, through a heap of at most k entries; ties keep the earlier record first."""
    heap = []
    for i, record in enumerate(records):
        heapq.heappush(heap, (record[field], -i, record))
        if len(heap) > k:
            heapq.heappop(heap)
    return [record for value, i, record in sorted(heap, key=lambda entry: (entry[0], entry[1]), reverse=True)]


def join(left, right, key):
    """Every left record merged with every right record sharing its key value, in left order: a hash join."""
    by_key = {}
    for record in right:
        by_key.setdefault(record[key], []).append(record)
    merged = []
    for record in left:
        for match in by_key.get(record[key], []):
            merged.append({**record, **match})
    return merged


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


def closest_name(query, names):
    """The name with the smallest edit distance to the query, and that distance; ties keep the first."""
    best, best_distance = None, None
    for name in names:
        distance = edit_distance(query, name)
        if best_distance is None or distance < best_distance:
            best, best_distance = name, distance
    return best, best_distance


def schedule(steps):
    """An order that runs every step after the steps it depends on (steps maps each step to its dependencies), taking ready steps in the order they became ready; ValueError if the steps form a cycle."""
    remaining = {step: len(deps) for step, deps in steps.items()}
    dependents = {step: [] for step in steps}
    for step, deps in steps.items():
        for dep in deps:
            dependents[dep].append(step)
    ready = deque(step for step in steps if remaining[step] == 0)
    order = []
    while ready:
        step = ready.popleft()
        order.append(step)
        for dependent in dependents[step]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                ready.append(dependent)
    if len(order) < len(steps):
        raise ValueError("the steps depend on each other in a cycle")
    return order


readings = [
    {"sensor": "s1", "value": 9},
    {"sensor": "s2", "value": 4},
    {"sensor": "s1", "value": 9},
    {"sensor": "s3", "value": 7},
]
places = [{"sensor": "s1", "room": "lab"}, {"sensor": "s3", "room": "hall"}]
unique = dedupe(readings, "sensor")
print(len(readings), "readings,", len(unique), "sensors")
print([row["sensor"] for row in top_k(unique, "value", 2)])
print([(row["sensor"], row["room"]) for row in join(unique, places, "sensor")])
print(edit_distance("kitten", "sitting"), closest_name("hal", ["lab", "hall"]))
print(schedule({"read": [], "calibrate": ["read"], "store": ["calibrate"], "plot": ["calibrate"]}))
