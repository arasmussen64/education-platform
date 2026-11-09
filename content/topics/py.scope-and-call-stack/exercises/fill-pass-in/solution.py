def total_with_tax(price, rate):
    return price + price * rate


def main():
    rate = 0.2
    print(total_with_tax(100, rate))


main()
