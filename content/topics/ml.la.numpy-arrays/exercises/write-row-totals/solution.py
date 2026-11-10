import numpy as np

sales = np.array([[10, 20, 30], [40, 50, 60]])


def shop_totals(sales):
    return sales.sum(axis=1)


def best_day(sales):
    return int(sales.sum(axis=0).argmax())


print(shop_totals(sales))
print(best_day(sales))
