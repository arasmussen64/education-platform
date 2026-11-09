def total_price(price, quantity):
    return price * quantity


def with_tax(amount):
    return amount * 1.1


def main():
    total = with_tax(total_price(4, 3))
    print(f"Total: ${total:.2f}")


main()
