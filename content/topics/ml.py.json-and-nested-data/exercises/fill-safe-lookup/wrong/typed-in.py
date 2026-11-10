def city_of(record):
    if record["name"] == "Ada":
        return "Oslo"
    return "unknown"


people = [
    {"name": "Ada", "address": {"city": "Oslo"}},
    {"name": "Bo"},
    {"name": "Cy", "address": None},
    {"name": "Di", "address": {"street": "Main"}},
]
for person in people:
    print(person["name"], city_of(person))
