deposit = 2400
rate = 0.04
years = 5

# One row per year, from the deposit in year 0 to the end of the last year.
balance = deposit
for year in range(years + 1):
    print(f"Year {year}: {balance:,.2f}")
    balance = balance + balance * rate
