start = 10000
growth = 0.07
fee = 0.01
years = 30

without = start
with_fee = start
for year in range(1, years + 1):
    without = without * (1 + growth)
    with_fee = with_fee * (1 + growth)
    with_fee = with_fee * (1 - fee)
    if year % 10 == 0:
        print(f"Year {year}: ${without:,.2f} without the fee, ${with_fee:,.2f} with it")

lost = (without - with_fee) / without
print(f"The fee took {lost:.1%}")
print(f"By the formula: {1 - (1 - fee) ** years:.1%}")
