values = [2, 4, 4, 4, 5, 5, 7, 9]
mean = sum(values) / len(values)
total = 0
for value in values:
    total = total + (value - mean) ** 2
variance = total / len(values)
spread = variance ** 0.5
print("mean", mean)
print("spread", spread)
