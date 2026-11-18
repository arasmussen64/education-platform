present = 1500
rate = 0.035
years = 4


def future_value(present, rate, periods):
    return present * (1 + rate) ** periods


for year in range(1, years + 1):
    print(f"Year {year}: {future_value(present, rate, year):,.2f}")
