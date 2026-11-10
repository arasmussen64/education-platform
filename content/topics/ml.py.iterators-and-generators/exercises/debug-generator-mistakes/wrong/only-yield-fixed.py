def squares(limit):
    n = 1
    while n <= limit:
        yield n * n
        n = n + 1


values = squares(4)
print(list(values))
print(sum(values))
print(max(values, default=0))
