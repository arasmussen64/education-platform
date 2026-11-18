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
    return yearly


def months_of_saving(start_age, retire_age):
    return (retire_age - start_age) * 12


nominal = growth_per_year(past_returns)
real = real_rate(nominal, inflation)
months = months_of_saving(start_age, retire_age)
balance = 0
for month in range(months):
    balance = balance * (1 + monthly_rate(real)) + monthly_saving

print(f"growth per year: {nominal * 100:.2f}%")
print(f"after inflation: {real * 100:.2f}%")
print(f"months of saving: {months}")
print(f"saved in all: {monthly_saving * months:,.2f}")
print(f"at {retire_age}, in today's money: {balance:,.2f}")
