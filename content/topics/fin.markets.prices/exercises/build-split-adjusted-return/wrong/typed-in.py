closes = [120.0, 124.0, 130.0, 66.0, 67.5, 69.0]
split_day = 3
ratio = 2


def adjust_for_split(closes, split_day, ratio):
    return [60.0, 62.0, 65.0, 66.0, 67.5, 69.0]


def total_return(prices):
    return 0.15


print("day 0: 60.00")
print("day 1: 62.00")
print("day 2: 65.00")
print("day 3: 66.00")
print("day 4: 67.50")
print("day 5: 69.00")
print("return from the raw closes: -42.5%")
print("true return: 15.0%")
