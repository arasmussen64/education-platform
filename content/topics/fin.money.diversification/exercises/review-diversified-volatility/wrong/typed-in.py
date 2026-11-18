import math

vol = 0.25
corr = 0.16


def diversified_volatility(vol, corr, n):
    return vol * math.sqrt(corr + (1 - corr) / n)


print("n = 1: 25.00%")
print("n = 2: 19.04%")
print("n = 5: 14.32%")
print("n = 10: 12.35%")
print("n = 100: 10.26%")
print("n = 1000: 10.03%")
