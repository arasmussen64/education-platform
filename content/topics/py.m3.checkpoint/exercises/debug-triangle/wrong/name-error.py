n = int(input("Height? "))
stars = 0
for row in range(1, n + 1):
    for _ in range(row):
        print("*", end="")
        stars += 1
    print()
print("Stars:", star)
