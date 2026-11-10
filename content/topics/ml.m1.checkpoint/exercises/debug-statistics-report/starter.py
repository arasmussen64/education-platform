values = [15, 4, 42, 8, 23, 16]

mean = sum(values) / (len(values) - 1)

middle = len(values) // 2
median = (values[middle - 1] + values[middle]) / 2

total = 0
for value in values:
    total = total + (value - mean) ** 2
spread = total / len(values)

print(f"mean {mean:.1f}")
print(f"median {median:.1f}")
print(f"spread {spread:.1f}")
