def f(x):
    return (x - 3) ** 2


x = 0
rate = 0.1
h = 0.000001
for step in range(30):
    slope = (f(x + h) - f(x)) / h
    x = x + rate * slope
print(round(x, 2))
