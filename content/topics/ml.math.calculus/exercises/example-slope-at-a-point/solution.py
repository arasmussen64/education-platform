def f(x):
    return x ** 2


h = 0.1
print(round((f(3 + h) - f(3)) / h, 4))

h = 0.001
print(round((f(3 + h) - f(3)) / h, 4))
