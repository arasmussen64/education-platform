n = int(input("Height? "))
for row in range(n):
    for _ in range(row):
        print("*", end="")
    print()
