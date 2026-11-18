principal = 15000
annual_rate = 0.072
months = 18
prices = [100.0, 104.0, 99.0, 106.0, 97.0, 103.0, 112.0]


def payment(principal, rate, periods):
    return principal * rate / (1 - (1 + rate) ** -periods)


def print_schedule(principal, annual_rate, months):
    rate = annual_rate / 12
    each = payment(principal, rate, months)
    balance = principal
    total_interest = 0
    for month in range(1, months + 1):
        interest = balance * rate
        repaid = each - interest
        balance = balance - repaid
        total_interest = total_interest + interest
        print(f"month {month}: interest {interest:,.2f}, principal {repaid:,.2f}, balance {balance:,.2f}")
    print(f"payment {each:,.2f}")
    print(f"total paid {each * months:,.2f}")
    print(f"total interest {total_interest:,.2f}")


def simple_returns(prices):
    # An empty list; for each position from 1 to the end, append the price
    # there divided by the one before, minus 1; return the list.
    ...


def annualized_return(prices, periods_per_year):
    # years = the number of periods (one fewer than the prices) divided by
    # periods_per_year; return (last / first) ** (1 / years) - 1.
    ...


def volatility(returns):
    # The mean of the returns; add up each return's squared distance from
    # it; divide by one less than the number of returns; return the square root.
    ...


def max_drawdown(prices):
    # Walk the positions keeping the position of the highest price so far
    # (the peak) and the largest fall from it, 1 - price / peak price, with
    # the positions of that peak and of the low; return all three.
    ...


print_schedule(principal, annual_rate, months)
print(f"annualized return {annualized_return(prices, 12) * 100:.1f}%")
print(f"volatility {volatility(simple_returns(prices)) * 12 ** 0.5 * 100:.1f}%")
drop = max_drawdown(prices)
print(f"max drawdown {drop[0] * 100:.1f}%, from position {drop[1]} to position {drop[2]}")
