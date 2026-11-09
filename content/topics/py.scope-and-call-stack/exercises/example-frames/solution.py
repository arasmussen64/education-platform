def double(n):
    result = n * 2
    return result


def describe(n):
    doubled = double(n)
    return f"{n} doubled is {doubled}"


def main():
    n = 5
    print(describe(n))
    print(n)


main()
