def squares(limit):
    n = 1
    while n <= limit:
        return n * n
        n = n + 1


values = squares(4)
print(list(values))
print(sum(values))
print(max(values))
