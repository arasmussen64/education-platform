total = 0
count = 0
while True:
    n = int(input("Number (0 to stop)? "))
    if n == 0:
        break
    total += n
    count += 1
print(f"{count} numbers, total {total}")
