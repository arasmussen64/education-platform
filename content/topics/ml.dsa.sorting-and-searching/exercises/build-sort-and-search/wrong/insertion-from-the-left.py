def insertion_sort(items):
    """A new sorted list: each item shifts left past the larger ones and stops at the first that isn't."""
    result = []
    for value in items:
        position = 0
        while position < len(result) and result[position] <= value:
            position += 1
        result.insert(position, value)
    return result


def merge_sort(items):
    """A new sorted list: split in half, sort each half, merge."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search(items, target):
    """The index of target in a sorted list, or -1."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def top_k_by(records, field, k):
    """The k records with the largest field value, largest first; ties keep their original order."""
    return sorted(records, key=lambda record: record[field], reverse=True)[:k]


print(insertion_sort([5, 2, 9, 1, 5, 6]), merge_sort([5, 2, 9, 1, 5, 6]))
print(binary_search([1, 3, 5, 7, 9], 7), binary_search([1, 3, 5, 7, 9], 4))
scores = [{"name": "ann", "score": 71}, {"name": "bob", "score": 93}, {"name": "cy", "score": 58}, {"name": "dee", "score": 93}]
print([record["name"] for record in top_k_by(scores, "score", 3)])
