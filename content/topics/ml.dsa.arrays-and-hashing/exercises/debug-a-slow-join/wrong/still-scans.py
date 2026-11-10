def group_by(records, field):
    groups = {}
    for record in records:
        groups.setdefault(record[field], []).append(record)
    return groups


def join(left, right, field):
    """Every left record merged with every right record sharing its field value, in left order."""
    merged = []
    for record in left:
        for match in right:
            if match[field] == record[field]:
                merged.append({**record, **match})
    return merged


people = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]
orders = [{"id": 2, "item": "lamp"}, {"id": 1, "item": "book"}, {"id": 2, "item": "pen"}]
print(join(people, orders, "id"))

left = [{"id": i} for i in range(2000)]
right = [{"id": i % 1000, "n": i} for i in range(2000)]
print(len(join(left, right, "id")))
