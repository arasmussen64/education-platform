def mean(values):
    return sum(values) / len(values)


def median(values):
    middle = len(values) // 2
    if len(values) % 2 == 1:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def spread(values):
    average = mean(values)
    total = 0
    for value in values:
        total = total + (value - average) ** 2
    return (total / len(values)) ** 0.5


scores = [68, 74, 74, 80, 90, 94]
print(f"Mean: {mean(scores):.1f}")
print(f"Median: {median(scores):.1f}")
print(f"Spread: {spread(scores):.1f}")
