smallest = 0
while True:
    n = int(input("Number (0 to stop)? "))
    if n == 0:
        break
    if n < smallest:
        smallest = n
print(smallest)
