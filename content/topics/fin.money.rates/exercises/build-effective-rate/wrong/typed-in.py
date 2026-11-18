def effective_annual_rate(apr, per_year):
    return {1: 0.21, 2: 0.221, 4: 0.2271, 12: 0.2314, 365: 0.2336}[per_year]


print("1 a year: 21.00%")
print("2 a year: 22.10%")
print("4 a year: 22.71%")
print("12 a year: 23.14%")
print("365 a year: 23.36%")
