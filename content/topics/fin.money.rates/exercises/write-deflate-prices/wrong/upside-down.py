# CPI-U yearly averages, BLS series CUUR0000SA0 (public domain), read 2026-11-17.
cpi = {1995: 152.4, 2000: 172.2, 2005: 195.3, 2010: 218.056, 2015: 237.017, 2020: 258.811, 2025: 321.943}
# A cinema ticket's price, by year (made up).
tickets = {2000: 5.40, 2010: 7.90, 2020: 9.20, 2025: 11.00}


def in_2025_dollars(price, year):
    return price * cpi[year] / cpi[2025]


for year, price in tickets.items():
    print(f"{year}: ${price:.2f} then, ${in_2025_dollars(price, year):.2f} in 2025 money")
