def total_with_tax(price, rate):
    """Return the price plus tax at the given rate."""
    return price + price * rate


def receipt_line(label, amount):
    """Return one line of a receipt, like 'Total: $12.00'."""
    return f"{label}: ${amount:.2f}"


def main():
    price = 20.0
    total = total_with_tax(price, 0.1)
    print(receipt_line("Price", price))
    print(receipt_line("Total", total))


main()
