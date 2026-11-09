text = input("Numbers? ")
count = 0
total = ""
largest = 0
digits = ""
for ch in text:
    if ch == " ":
        count += 1
        total += digits
        if int(digits) > largest:
            largest = int(digits)
        digits = ""
    else:
        digits = digits + ch
count += 1
total += digits
if int(digits) > largest:
    largest = int(digits)
print(f"Numbers: {count}")
print(f"Total: {total}")
print(f"Largest: {largest}")
digits = ""
for ch in text:
    if ch == " ":
        for _ in range(int(digits)):
            print("#", end="")
        print()
        digits = ""
    else:
        digits = digits + ch
for _ in range(int(digits)):
    print("#", end="")
print()
