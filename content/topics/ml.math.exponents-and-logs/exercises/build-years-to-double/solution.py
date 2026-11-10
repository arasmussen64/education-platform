def years_to_double(rate):
    amount = 1.0
    years = 0
    while amount < 2.0:
        amount = amount * (1 + rate / 100)
        years = years + 1
    return years


for rate in (2, 5, 10):
    print(f"{rate}%: {years_to_double(rate)} years")
