width = int(input("Width? "))
height = int(input("Height? "))
for _ in range(width):
    for _ in range(height):
        print("*", end="")
    print()
