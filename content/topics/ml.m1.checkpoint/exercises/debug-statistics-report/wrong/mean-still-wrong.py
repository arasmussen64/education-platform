values = [15, 4, 42, 8, 23, 16]

mean = sum(values) / (len(values) - 1)

ordered = sorted(values)
middle = len(ordered) // 2
median = (ordered[middle - 1] + ordered[middle]) / 2

total = 0
for value in values:
    total = total + (value - mean) ** 2
spread = (total / len(values)) ** 0.5

print(f"mean {mean:.1f}")
print(f"median {median:.1f}")
print(f"spread {spread:.1f}")
