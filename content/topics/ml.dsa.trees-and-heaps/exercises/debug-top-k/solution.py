import heapq


def top_k(values, k):
    """The k largest values, largest first, keeping only k values in the heap at a time."""
    heap = []
    for value in values:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


readings = [12, 95, 3, 88, 41, 95, 7, 66, 23, 50]
print(top_k(readings, 3))
print(top_k(readings, 1), top_k(readings, 10))
