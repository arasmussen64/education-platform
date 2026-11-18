def simple_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        returns.append(prices[i] / prices[i - 1] - 1)
    return returns


def annualized_return(prices, periods_per_year):
    years = (len(prices) - 1) / periods_per_year
    return (prices[-1] / prices[0]) ** (1 / years) - 1


prices = [100, 112, 95, 118, 130]
returns = simple_returns(prices)
for i in range(len(returns)):
    print(f"Year {i + 1}: {returns[i]:.2%}")
print(f"Annualized: {annualized_return(prices, 1):.2%}")
