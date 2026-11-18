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
print("Without the fee: $135,454.20")
print("With the fee: $100,165.02")
print("The fee takes 26.1% of what you'd have had")
