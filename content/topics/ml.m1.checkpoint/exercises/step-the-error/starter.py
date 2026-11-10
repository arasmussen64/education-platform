xs = [1, 2, 3, 4, 5]
ys = [3, 5, 7, 9, 11]


def predict(m, b, x):
    return m * x + b


def error(m, b, xs, ys):
    total = 0
    for i in range(len(xs)):
        total = total + (predict(m, b, xs[i]) ... ys[i]) ... 2
    return total ... len(xs)


print(error(0, 0, xs, ys))
print(error(2, 1, xs, ys))
