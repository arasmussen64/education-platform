width = int(input("Width? "))
height = int(input("Height? "))
for _ in range(height):
    for _ in range(width):
        print("*", end="")
    print()
