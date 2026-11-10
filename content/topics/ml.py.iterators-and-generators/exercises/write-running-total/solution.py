def running_total(numbers):
    total = 0
    for n in numbers:
        total = total + n
        yield total


print(list(running_total([1, 2, 3, 4])))
