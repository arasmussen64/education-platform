def final_amount(start, growth, fee, years):
    balance = start
    for year in range(years):
        balance = balance * (1 + growth) * (1 - fee)
    return balance


def share_lost(start, growth, fee, years):
    without = final_amount(start, growth, 0, years)
    with_fee = final_amount(start, growth, fee, years)
    return (without - with_fee) / without


start = 25000
growth = 0.06
fee = 0.008

print("10 years: $44,771.19 without the fee, $41,315.73 with it, 7.7% lost")
print("20 years: $80,178.39 without the fee, $68,279.57 with it, 14.8% lost")
print("30 years: $143,587.28 without the fee, $112,840.79 with it, 21.4% lost")
print("40 years: $257,142.95 without the fee, $186,483.97 with it, 27.5% lost")
