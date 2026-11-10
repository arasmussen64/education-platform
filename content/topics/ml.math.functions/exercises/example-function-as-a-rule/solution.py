def f(x):
    return 2 * x + 1


print(f(3))
print(f(0))
print(f(-2))

for x in range(0, 4):
    print(x, f(x))
