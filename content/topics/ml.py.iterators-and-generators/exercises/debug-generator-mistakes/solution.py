def squares(limit):
    n = 1
    while n <= limit:
        yield n * n
        n = n + 1


values = list(squares(4))
print(values)
print(sum(values))
print(max(values))
