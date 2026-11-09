n = int(input("Size? "))
for row in range(1, n):
    for col in range(1, n + 1):
        print(row * col, end=" ")
    print()
