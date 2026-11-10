def city_of(record):
    address = record.get(...)
    if not isinstance(address, ...):
        return "unknown"
    return address.get("city", ...)


people = [
    {"name": "Ada", "address": {"city": "Oslo"}},
    {"name": "Bo"},
    {"name": "Cy", "address": None},
    {"name": "Di", "address": {"street": "Main"}},
]
for person in people:
    print(person["name"], city_of(person))
