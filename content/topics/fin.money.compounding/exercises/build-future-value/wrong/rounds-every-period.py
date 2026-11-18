present = 1500
rate = 0.035
years = 4


def future_value(present, rate, periods):
    balance = present
    for period in range(periods):
        balance = round(balance * (1 + rate))
    return balance


for year in range(years + 1):
    print(f"Year {year}: {future_value(present, rate, year):,.2f}")
