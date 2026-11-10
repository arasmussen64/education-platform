def windows(values, size):
    for start in range(len(values) - size):
        yield values[start:start + size]


print(list(windows([1, 2, 3, 4, 5], 3)))
