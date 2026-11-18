savings = 3000
rate = 0.05
years = 4

balance = savings
print(f"Year 0: {balance:,.2f}")
for year in range(1, years + 1):
    balance = balance * (1 + rate)
    print(f"Year {year}: {balance:,.2f}")
