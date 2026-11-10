x = 2.0
v = 0.0


def momentum_step(x, v, g, rate, beta):
    v = beta * v + g
    return x - rate * v, v


for step in range(2):
    x, v = momentum_step(x, v, 2 * x, 0.1, 0.5)
    print(x)
