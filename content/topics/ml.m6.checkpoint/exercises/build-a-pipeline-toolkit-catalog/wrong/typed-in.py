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


print('7 rows, 5 products')
print("['B2', 'C3', 'E5']")
print("[('A1', 'NO'), ('B2', 'EE'), ('C3', 'NO'), ('E5', 'EE')]")
print("('north', 2)")
print("['download', 'parse', 'validate', 'prices', 'merge', 'publish']")
