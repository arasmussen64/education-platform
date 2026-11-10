def group_by(records, field):
    """{value of the field: [the records with that value]}, first appearance first."""
    groups = {}
    for record in records:
        groups.setdefault(record[...], ...).append(record)
    return groups


orders = [
    {"id": 1, "city": "Oslo", "total": 30},
    {"id": 2, "city": "Lima", "total": 12},
    {"id": 3, "city": "Oslo", "total": 8},
    {"id": 4, "city": "Pune", "total": 19},
    {"id": 5, "city": "Lima", "total": 41},
]
for city, group in group_by(orders, "city").items():
    print(city, len(group), sum(order["total"] for order in group))
