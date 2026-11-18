# CPI-U yearly averages, BLS series CUUR0000SA0 (public domain), read 2026-11-17.
cpi = {2019: 255.657, 2020: 258.811, 2021: 270.970, 2022: 292.655, 2023: 304.702, 2024: 313.689, 2025: 321.943}

start_year = 2022
end_year = 2024
invested = 10000
nominal = 0.12

inflation = cpi[end_year] / cpi[start_year] - 1
inflation_pct = inflation * 100
final = invested * (1 + nominal)
needed = invested * cpi[start_year] / cpi[end_year]
real = (1 + nominal) / (1 + inflation) - 1

print(f"Prices rose {inflation_pct:.2f}% from {start_year} to {end_year}.")
print(f"Your ${invested:,} grew to ${final:,.2f}.")
print(f"To keep up with prices it needed ${needed:,.2f}.")
print(f"Real return: {real:.2%}")
