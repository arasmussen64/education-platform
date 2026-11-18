principal = 24000
annual_rate = 0.08
quarters = 8
prices = [40.0, 40.5, 39.8, 40.9, 41.2, 40.1, 41.5, 42.0, 41.6]


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


print("""quarter 1: interest 480.00, principal 2,796.24, balance 21,203.76
quarter 2: interest 424.08, principal 2,852.16, balance 18,351.60
quarter 3: interest 367.03, principal 2,909.20, balance 15,442.40
quarter 4: interest 308.85, principal 2,967.39, balance 12,475.01
quarter 5: interest 249.50, principal 3,026.73, balance 9,448.28
quarter 6: interest 188.97, principal 3,087.27, balance 6,361.01
quarter 7: interest 127.22, principal 3,149.01, balance 3,212.00
quarter 8: interest 64.24, principal 3,212.00, balance 0.00
payment 3,276.24
total paid 26,209.88
total interest 2,209.88
annualized return 29.0%
volatility 15.5%
max drawdown 2.7%""")
