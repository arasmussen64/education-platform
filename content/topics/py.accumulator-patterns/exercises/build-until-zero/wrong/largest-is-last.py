count = 0
total = 0
largest = 0
while True:
    n = int(input("Number (0 to stop)? "))
    if n == 0:
        break
    count += 1
    total += n
    largest = n
print(f"Count: {count}")
print(f"Total: {total}")
print(f"Largest: {largest}")
