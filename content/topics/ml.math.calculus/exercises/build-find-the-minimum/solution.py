def loss(x):
    return (x - 2) ** 2 + 1


def slope_at(x):
    h = 0.000001
    return (loss(x + h) - loss(x)) / h


def minimize(start, rate, steps):
    x = start
    for step in range(steps):
        x = x - rate * slope_at(x)
    return x


best = minimize(10, 0.1, 50)
print(f"Lowest at x = {round(best, 3)}, loss = {round(loss(best), 3)}")
