def length(v):
    total = 0
    for value in v:
        total = total + value * value
    return total ** 0.5


print(length([3, 4]))
print(length([1, 2, 2]))
print(length([6, 8]))
