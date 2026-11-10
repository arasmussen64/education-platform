def dedupe(records, key):
    """The first record for each value of the key field, in order."""
    seen = ...
    kept = []
    for record in records:
        if record[key] not in seen:
            seen....(record[key])
            kept.append(record)
    return kept


records = [{"id": 7, "spend": 40}, {"id": 3, "spend": 15}, {"id": 7, "spend": 40}, {"id": 9, "spend": 70}, {"id": 3, "spend": 15}]
print([record["id"] for record in dedupe(records, "id")])
