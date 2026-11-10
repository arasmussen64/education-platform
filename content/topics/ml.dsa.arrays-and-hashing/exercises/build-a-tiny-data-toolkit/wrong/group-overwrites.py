def count_frequencies(items):
    """{value: how many times it appears}, in one pass."""
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def dedupe(items):
    """The distinct values, first appearance first."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def group_by(records, field):
    """{value of the field: [the records with that value]}."""
    groups = {}
    for record in records:
        groups[record[field]] = [record]
    return groups


def join(left, right, field):
    """Every left record merged with every right record sharing its field value (right's fields win), in left order."""
    by_key = group_by(right, field)
    merged = []
    for record in left:
        for match in by_key.get(record[field], []):
            merged.append({**record, **match})
    return merged


words = "the cat sat on the mat the end".split()
print(count_frequencies(words))
print(dedupe(words))
people = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}, {"id": 3, "name": "Linus"}]
orders = [{"id": 2, "item": "lamp"}, {"id": 1, "item": "book"}, {"id": 2, "item": "pen"}, {"id": 9, "item": "cup"}]
print(sorted(group_by(orders, "id")))
print(join(people, orders, "id"))
