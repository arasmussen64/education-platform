def average(a, b):
    return (a + b) / 2


def describe(a, b):
    return f"The average of {a} and {b} is {average(a, b)}"


def main():
    print(describe(4, 8))
    print(describe(3, 4))


main()
