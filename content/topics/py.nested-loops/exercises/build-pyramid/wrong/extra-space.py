n = int(input("Height? "))
for row in range(1, n + 1):
    for _ in range(n - row + 1):
        print(" ", end="")
    for _ in range(row):
        print("#", end="")
    print()
