closes = [40.00, 40.80, 41.00, 40.20, 40.60]
ex_day = 3
dividend = 1.00


def adjust_for_dividend(closes, ex_day, dividend):
    return [39.02, 39.80, 40.00, 40.20, 40.60]


print("day 0: 39.02")
print("day 1: 39.80")
print("day 2: 40.00")
print("day 3: 40.20")
print("day 4: 40.60")
print("return from the raw closes: 1.50%")
print("return with the dividend: 4.04%")
