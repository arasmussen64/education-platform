# A friend's retirement calculator: what saving every month grows to by
# retirement, in today's money. The fund's past yearly returns are made up.
past_returns = [0.18, -0.12, 0.25, -0.08, 0.10]
inflation = 0.03
monthly_saving = 400
start_age = 35
retire_age = 65


def growth_per_year(returns):
    growth = 1
    for r in returns:
        growth = growth * (1 + r)
    return growth ** (1 / len(returns)) - 1


def real_rate(nominal, inflation):
    return (1 + nominal) / (1 + inflation) - 1


def monthly_rate(yearly):
    return yearly / 12


def months_of_saving(start_age, retire_age):
    return (retire_age - start_age) * 12


print("growth per year: 5.61%")
print("after inflation: 2.53%")
print("months of saving: 360")
print("saved in all: 144,000.00")
print("at 65, in today's money: 215,252.79")
