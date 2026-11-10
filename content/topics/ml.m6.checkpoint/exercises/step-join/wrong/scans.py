def join(left, right, key):
    """Every left record merged with every right record sharing its key value, in left order."""
    merged = []
    for record in left:
        for match in right:
            if match[key] == record[key]:
                merged.append({**record, **match})
    return merged


users = [{"user": "ann", "city": "Oslo"}, {"user": "bob", "city": "Lima"}]
events = [{"id": 1, "user": "ann"}, {"id": 2, "user": "cy"}, {"id": 3, "user": "bob"}, {"id": 4, "user": "ann"}]
print([(row["id"], row["city"]) for row in join(events, users, "user")])
