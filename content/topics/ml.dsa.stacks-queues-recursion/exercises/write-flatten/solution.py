def flatten(nested):
    """Every non-list value in a nest of lists, in order."""
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


print(flatten([1, [2, [3, 4]], [], [[5]], 6]))
print(flatten([]))
print(flatten([[[]], "a"]))
