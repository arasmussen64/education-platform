xs = [1, 2, 3, 4, 5]
ys = [3, 5, 7, 9, 11]


def predict(m, b, x):
    return m * x + b


def slopes(m, b, xs, ys):
    slope_m = 0
    slope_b = 0
    for i in range(len(xs)):
        miss = predict(m, b, xs[i]) - ys[i]
        slope_m = slope_m + 2 * miss * xs[i]
        slope_b = slope_b + 2 * miss
    return [slope_m / len(xs), slope_b / len(xs)]


m = 0.0
b = 0.0
rate = 0.05
current = slopes(m, b, xs, ys)
m = m - rate * current[0]
b = b - rate * current[1]
print(round(m, 2), round(b, 2))
