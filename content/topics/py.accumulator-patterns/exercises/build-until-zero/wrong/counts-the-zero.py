count = 0
total = 0
largest = 0
while True:
    n = int(input("Number (0 to stop)? "))
    count += 1
    if n == 0:
        break
    total += n
    if n > largest:
        largest = n
print(f"Count: {count}")
print(f"Total: {total}")
print(f"Largest: {largest}")
