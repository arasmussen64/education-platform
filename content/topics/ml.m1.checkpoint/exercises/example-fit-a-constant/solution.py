ys = [3, 5, 7, 9, 11]


def error(c):
    total = 0
    for y in ys:
        total = total + (c - y) ** 2
    return total / len(ys)


print("error at 0:", error(0))


def slope(c):
    total = 0
    for y in ys:
        total = total + 2 * (c - y)
    return total / len(ys)


print("slope at 0:", slope(0))

c = 0.0
rate = 0.1
for step in range(100):
    c = c - rate * slope(c)

print("best c:", round(c, 2))
print("error there:", round(error(c), 2))
