def largest(a, b):
    if a > b:
        return a
    else:
        print(b)


def sum_to(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total


def half(n):
    return n / 2


def main():
    print(largest(3, 8))
    print(largest(9, 2))
    print(sum_to(4))
    print(half(10))


main()
