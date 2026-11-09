percent = 25


def apply_discount(price, unused):
    return round(price - price * percent / 100, 2)
