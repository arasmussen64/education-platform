products = [("cake", 4.0), ("jam", 6.5), ("tea", 2.5)]
cheapest_first = sorted(products, key=lambda p: p[0])
print(cheapest_first)
priciest = max(products, key=lambda p: p)
print(priciest[0])
