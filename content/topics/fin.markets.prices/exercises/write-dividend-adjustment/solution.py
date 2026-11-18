closes = [40.00, 40.80, 41.00, 40.20, 40.60]
ex_day = 3
dividend = 1.00


def adjust_for_dividend(closes, ex_day, dividend):
    factor = 1 - dividend / closes[ex_day - 1]
    adjusted = []
    for i in range(len(closes)):
        if i < ex_day:
            adjusted.append(closes[i] * factor)
        else:
            adjusted.append(closes[i])
    return adjusted


adjusted = adjust_for_dividend(closes, ex_day, dividend)
for i in range(len(adjusted)):
    print(f"day {i}: {adjusted[i]:.2f}")
print(f"return from the raw closes: {(closes[-1] / closes[0] - 1) * 100:.2f}%")
print(f"return with the dividend: {(adjusted[-1] / adjusted[0] - 1) * 100:.2f}%")
