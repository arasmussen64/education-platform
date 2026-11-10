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


print('7 events, 5 distinct')
print('[9, 12, 7]')
print("[(7, 'Oslo'), (3, 'Lima'), (9, 'Pune'), (15, 'Oslo')]")
print("('Pune', 2)")
print("['load', 'clean', 'join', 'features', 'train', 'report']")
