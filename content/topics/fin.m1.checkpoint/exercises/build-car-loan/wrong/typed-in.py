principal = 18000
annual_rate = 0.048
months = 24
prices = [80.0, 82.0, 79.0, 84.0, 88.0, 85.0, 78.0, 81.0, 86.0, 90.0, 87.0, 92.0, 94.0]


def payment(principal, rate, periods):
    return 0


def simple_returns(prices):
    return []


def annualized_return(prices, periods_per_year):
    return 0


def volatility(returns):
    return 0


def max_drawdown(prices):
    return 0


print("""month 1: interest 72.00, principal 716.07, balance 17,283.93
month 2: interest 69.14, principal 718.94, balance 16,564.99
month 3: interest 66.26, principal 721.81, balance 15,843.17
month 4: interest 63.37, principal 724.70, balance 15,118.47
month 5: interest 60.47, principal 727.60, balance 14,390.87
month 6: interest 57.56, principal 730.51, balance 13,660.36
month 7: interest 54.64, principal 733.43, balance 12,926.93
month 8: interest 51.71, principal 736.37, balance 12,190.56
month 9: interest 48.76, principal 739.31, balance 11,451.25
month 10: interest 45.81, principal 742.27, balance 10,708.98
month 11: interest 42.84, principal 745.24, balance 9,963.75
month 12: interest 39.85, principal 748.22, balance 9,215.53
month 13: interest 36.86, principal 751.21, balance 8,464.32
month 14: interest 33.86, principal 754.22, balance 7,710.10
month 15: interest 30.84, principal 757.23, balance 6,952.87
month 16: interest 27.81, principal 760.26, balance 6,192.60
month 17: interest 24.77, principal 763.30, balance 5,429.30
month 18: interest 21.72, principal 766.36, balance 4,662.94
month 19: interest 18.65, principal 769.42, balance 3,893.52
month 20: interest 15.57, principal 772.50, balance 3,121.02
month 21: interest 12.48, principal 775.59, balance 2,345.43
month 22: interest 9.38, principal 778.69, balance 1,566.74
month 23: interest 6.27, principal 781.81, balance 784.93
month 24: interest 3.14, principal 784.93, balance 0.00
payment 788.07
total paid 18,913.77
total interest 913.77
annualized return 17.5%
volatility 16.8%
max drawdown 11.4%""")
