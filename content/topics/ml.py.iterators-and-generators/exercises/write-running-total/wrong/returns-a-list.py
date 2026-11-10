def running_total(numbers):
    totals = []
    total = 0
    for n in numbers:
        total = total + n
        totals.append(total)
    return totals


print(list(running_total([1, 2, 3, 4])))
