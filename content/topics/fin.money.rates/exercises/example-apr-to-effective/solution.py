apr = 0.24
per_year = 12
monthly = apr / per_year
balance = 1000.0
for month in range(per_year):
    balance = balance * (1 + monthly)
effective = balance / 1000 - 1
print(f"Charged each month: {monthly:.2%}")
print(f"$1,000 after a year: ${balance:,.2f}")
print(f"Effective annual rate: {effective:.2%}")
print(f"By the formula: {(1 + monthly) ** per_year - 1:.2%}")
