def windows(values, size):
    result = []
    for start in range(len(values) - size + 1):
        result.append(values[start:start + size])
    return result


print(list(windows([1, 2, 3, 4, 5], 3)))
