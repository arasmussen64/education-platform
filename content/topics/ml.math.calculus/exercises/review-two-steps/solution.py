x = 0.0
rate = 0.25
for step in range(2):
    slope = 2 * (x - 4)
    x = x - rate * slope
    print(x)
