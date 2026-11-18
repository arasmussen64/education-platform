principal = 24000
annual_rate = 0.08
quarters = 8
prices = [40.0, 40.5, 39.8, 40.9, 41.2, 40.1, 41.5, 42.0, 41.6]


def payment(principal, rate, periods):
    return principal * rate / (1 - (1 + rate) ** -periods)


def print_schedule(principal, annual_rate, quarters):
    rate = annual_rate / 4
    each = payment(principal, rate, quarters)
    balance = principal
    total_interest = 0
    for quarter in range(1, quarters + 1):
        interest = balance * rate
        repaid = each - interest
        balance = balance - repaid
        total_interest = total_interest + interest
        print(f"quarter {quarter}: interest {interest:,.2f}, principal {repaid:,.2f}, balance {balance:,.2f}")
    print(f"payment {each:,.2f}")
    print(f"total paid {each * quarters:,.2f}")
    print(f"total interest {total_interest:,.2f}")


def simple_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        returns.append(prices[i] / prices[i - 1] - 1)
    return returns


def annualized_return(prices, periods_per_year):
    years = (len(prices) - 1) / periods_per_year
    return (prices[-1] / prices[0]) ** (1 / years) - 1


def volatility(returns):
    mean = sum(returns) / len(returns)
    total = 0
    for r in returns:
        total = total + (r - mean) ** 2
    return (total / (len(returns) - 1)) ** 0.5


def max_drawdown(prices):
    peak = prices[0]
    worst = 0
    for price in prices:
        peak = max(peak, price)
        worst = max(worst, 1 - price / peak)
    return worst


print_schedule(principal, annual_rate, quarters)
print(f"annualized return {annualized_return(prices, 52) * 100:.1f}%")
print(f"volatility {volatility(simple_returns(prices)) * 52 ** 0.5 * 100:.1f}%")
print(f"max drawdown {max_drawdown(prices) * 100:.1f}%")
