def first_squares(count):
    n = 1
    while n <= count:
        yield n * n
        n = n + 1


print(list(first_squares(4)))
