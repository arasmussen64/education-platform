def compose(f, g):
    def both(x):
        return f(g(x))

    return both


def increment(x):
    return x + 1


def double(x):
    return x * 2


print(compose(increment, double)(5))
print(compose(double, increment)(5))
