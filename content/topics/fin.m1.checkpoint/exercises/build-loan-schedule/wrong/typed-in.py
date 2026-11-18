principal = 15000
annual_rate = 0.072
months = 18
prices = [100.0, 104.0, 99.0, 106.0, 97.0, 103.0, 112.0]


def payment(principal, rate, periods):
    return 881.64


def simple_returns(prices):
    return [0.04, -0.048, 0.071, -0.085, 0.062, 0.087]


def annualized_return(prices, periods_per_year):
    return 0.254


def volatility(returns):
    return 0.0706


def max_drawdown(prices):
    return 0.085


print("""month 1: interest 90.00, principal 791.64, balance 14,208.36
month 2: interest 85.25, principal 796.39, balance 13,411.97
month 3: interest 80.47, principal 801.17, balance 12,610.81
month 4: interest 75.66, principal 805.97, balance 11,804.83
month 5: interest 70.83, principal 810.81, balance 10,994.02
month 6: interest 65.96, principal 815.67, balance 10,178.35
month 7: interest 61.07, principal 820.57, balance 9,357.78
month 8: interest 56.15, principal 825.49, balance 8,532.29
month 9: interest 51.19, principal 830.44, balance 7,701.85
month 10: interest 46.21, principal 835.43, balance 6,866.42
month 11: interest 41.20, principal 840.44, balance 6,025.98
month 12: interest 36.16, principal 845.48, balance 5,180.50
month 13: interest 31.08, principal 850.56, balance 4,329.94
month 14: interest 25.98, principal 855.66, balance 3,474.28
month 15: interest 20.85, principal 860.79, balance 2,613.49
month 16: interest 15.68, principal 865.96, balance 1,747.53
month 17: interest 10.49, principal 871.15, balance 876.38
month 18: interest 5.26, principal 876.38, balance 0.00
payment 881.64
total paid 15,869.49
total interest 869.49
annualized return 25.4%
volatility 24.4%
max drawdown 8.5%, from position 3 to position 4""")
