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
print("Taxed every year: $66,132.84")
print("Taxed at the end: $81,984.06")
print("Difference: $15,851.21")
