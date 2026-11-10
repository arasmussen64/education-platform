def merge(left, right):
    """Combine two sorted lists into one sorted list in a single pass."""
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
    return merged


print(merge([1, 4, 9], [2, 3, 10, 11]))
print(merge([], [5, 6]))
print(merge([2, 2], [2]))
