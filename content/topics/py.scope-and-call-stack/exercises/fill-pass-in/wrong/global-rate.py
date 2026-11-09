rate = 0.2


def total_with_tax(price, unused):
    return price + price * rate


def main():
    print(total_with_tax(100, rate))


main()
