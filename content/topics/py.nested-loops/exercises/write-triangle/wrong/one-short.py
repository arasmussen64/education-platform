n = int(input("Height? "))
for row in range(1, n):
    for _ in range(row):
        print("*", end="")
    print()
