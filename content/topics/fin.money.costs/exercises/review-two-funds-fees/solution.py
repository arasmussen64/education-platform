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


a = final_amount(start, growth, fee_a, years)
b = final_amount(start, growth, fee_b, years)
better = max(a, b)
worse = min(a, b)
print(f"Fund A: ${a:,.2f}")
print(f"Fund B: ${b:,.2f}")
print(f"Difference: {(better - worse) / better:.1%} of the better fund's amount")
