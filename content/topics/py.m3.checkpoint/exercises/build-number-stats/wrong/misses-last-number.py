text = input("Numbers? ")
count = 0
total = 0
largest = 0
digits = ""
for ch in text:
    if ch == " ":
        number = int(digits)
        count += 1
        total += number
        if number > largest:
            largest = number
        digits = ""
    else:
        digits = digits + ch
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
