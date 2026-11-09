a = 4
b = 8


def average(x, y):
    return (x + y) / 2


def describe(x, y):
    return f"The average of {a} and {b} is {average(a, b)}"


def main():
    print(describe(4, 8))
    print(describe(3, 4))


main()
