closes = [120.0, 124.0, 130.0, 66.0, 67.5, 69.0]
split_day = 3
ratio = 2


def adjust_for_split(closes, split_day, ratio):
    adjusted = []
    for i in range(len(closes)):
        if i <= split_day:
            adjusted.append(closes[i] / ratio)
        else:
            adjusted.append(closes[i])
    return adjusted


def total_return(prices):
    return prices[-1] / prices[0] - 1


adjusted = adjust_for_split(closes, split_day, ratio)
for i in range(len(adjusted)):
    print(f"day {i}: {adjusted[i]:.2f}")
print(f"return from the raw closes: {total_return(closes) * 100:.1f}%")
print(f"true return: {total_return(adjusted) * 100:.1f}%")
