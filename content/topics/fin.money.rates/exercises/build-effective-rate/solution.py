def effective_annual_rate(apr, per_year):
    return (1 + apr / per_year) ** per_year - 1


for per_year in [1, 2, 4, 12, 365]:
    print(f"{per_year} a year: {effective_annual_rate(0.21, per_year):.2%}")
