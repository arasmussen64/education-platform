def amount_to_pay(total):
    """Return the total after the spec's discount, rounded to cents."""
    if total >= 100:
        rate = 0.10
    elif total >= 50:
        rate = 0.05
    else:
        rate = 0
    return total * (1 - rate)
