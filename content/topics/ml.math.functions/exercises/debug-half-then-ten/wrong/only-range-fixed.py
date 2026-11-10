def half(x):
    return x // 2


def plus_ten(x):
    return x + 10


print(plus_ten(half(8)))

for x in range(1, 4):
    print(x, plus_ten(half(x)))
