def square(n):
    return n * n


def main():
    print(square(3))
    area = square(4)
    print(f"A 4 by 4 square has area {area}")
    print(square(square(2)))


main()
