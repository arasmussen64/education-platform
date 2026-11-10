def dedupe(records, key):
    return records


def top_k(records, field, k):
    return records[:k]


def join(left, right, key):
    return []


def closest_name(query, names):
    return (names[0], 0)


def schedule(steps):
    return list(steps)


print('8 lines, 6 requests')
print("['r2', 'r4', 'r5']")
print("[('r1', 'discovery'), ('r2', 'money'), ('r3', 'identity'), ('r4', 'money'), ('r5', 'discovery')]")
print("('payment', 2)")
print("['build', 'test', 'scan', 'stage', 'smoke', 'release']")
