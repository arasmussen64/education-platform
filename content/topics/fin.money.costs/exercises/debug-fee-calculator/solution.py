start = 40000
growth = 0.05
fee = 0.012
years = 25

without = start
for year in range(years):
    without = without * (1 + growth)

with_fee = start
for year in range(years):
    with_fee = with_fee * (1 + growth) * (1 - fee)

lost = (without - with_fee) / without
print(f"Without the fee: ${without:,.2f}")
print(f"With the fee: ${with_fee:,.2f}")
print(f"The fee takes {lost:.1%} of what you'd have had")
