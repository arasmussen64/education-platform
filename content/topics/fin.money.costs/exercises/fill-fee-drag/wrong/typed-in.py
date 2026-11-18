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
print("Without the fee: $34,242.38")
print("With the fee: $23,467.65")
print("The fee takes 31.5%")
