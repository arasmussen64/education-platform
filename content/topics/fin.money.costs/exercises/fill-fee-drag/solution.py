start = 5000
growth = 0.08
fee = 0.015
years = 25

without = start
with_fee = start
for year in range(years):
    without = without * (1 + growth)
    with_fee = with_fee * (1 + growth) * (1 - fee)

lost = (without - with_fee) / without
print(f"Without the fee: ${without:,.2f}")
print(f"With the fee: ${with_fee:,.2f}")
print(f"The fee takes {lost:.1%}")
