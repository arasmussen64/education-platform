import heapq


def top_k(records, field, k):
    """The k records with the largest field value, largest first, through a heap of at most k entries."""
    heap = []
    for i, record in enumerate(records):
        heapq.heappush(heap, (record[field], -i, record))
        if len(heap) > k:
            heapq.heappop(heap)
    return [record for value, i, record in sorted(heap, key=lambda entry: (entry[0], entry[1]), reverse=True)]


records = [{"id": 7, "spend": 40}, {"id": 3, "spend": 15}, {"id": 7, "spend": 40}, {"id": 9, "spend": 70}, {"id": 3, "spend": 15}]
print([record["id"] for record in top_k(records, "spend", 2)])
print([record["id"] for record in top_k(records, "spend", 10)])
