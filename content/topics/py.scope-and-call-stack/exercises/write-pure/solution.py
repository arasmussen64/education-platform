def apply_discount(price, percent):
    discount = price * percent / 100
    return round(price - discount, 2)
