def final_amount(start, growth, fee, years):
    balance = start
    for year in range(1, years):
        balance = balance * (1 + growth) * (1 - fee)
    return balance


def share_lost(start, growth, fee, years):
    without = final_amount(start, growth, 0, years)
    with_fee = final_amount(start, growth, fee, years)
    return (without - with_fee) / without


start = 25000
growth = 0.06
fee = 0.008

for years in [10, 20, 30, 40]:
    without = final_amount(start, growth, 0, years)
    with_fee = final_amount(start, growth, fee, years)
    lost = share_lost(start, growth, fee, years)
    print(f"{years} years: ${without:,.2f} without the fee, ${with_fee:,.2f} with it, {lost:.1%} lost")
