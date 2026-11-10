it = iter([10, 20])
print(next(it))
print(next(it))


def countdown(n):
    while n > 0:
        yield n
        n = n - 1


for value in countdown(3):
    print(value)


squares = (n * n for n in range(4))
print(sum(squares))
print(list(squares))
