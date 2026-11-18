start = 20000
growth = 0.07
tax = 0.30
years = 25


def taxed_every_year(start, growth, tax, years):
    balance = start
    for year in range(years):
        gain = balance * growth
        balance = balance + gain * (1 - tax)
    return balance


def taxed_at_the_end(start, growth, tax, years):
    balance = start
    for year in range(years):
        balance = balance * (1 + growth)
    gain = balance - start
    return balance - gain * tax


every_year = taxed_every_year(start, growth, tax, years)
at_the_end = taxed_at_the_end(start, growth, tax, years)
print(f"Taxed every year: ${every_year:,.2f}")
print(f"Taxed at the end: ${at_the_end:,.2f}")
print(f"Difference: ${at_the_end - every_year:,.2f}")
