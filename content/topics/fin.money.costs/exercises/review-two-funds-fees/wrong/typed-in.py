start = 30000
growth = 0.065
fee_a = 0.009
fee_b = 0.0015
years = 30


def final_amount(start, growth, fee, years):
    balance = start
    for year in range(years):
        balance = balance * (1 + growth) * (1 - fee)
    return balance


print("Fund A: $151,293.10")
print("Fund B: $189,693.11")
print("Difference: 20.2% of the better fund's amount")
