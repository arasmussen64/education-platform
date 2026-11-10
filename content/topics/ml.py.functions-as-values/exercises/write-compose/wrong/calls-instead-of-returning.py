def compose(f, g):
    def both(x):
        return f(g(x))

    return both(5)


def increment(x):
    return x + 1


def double(x):
    return x * 2


print(compose(increment, double))
print(compose(double, increment))
