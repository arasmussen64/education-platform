# Read the numbers
text = input("Numbers? ")

# Count them, add them up, and find the largest
count = 0
total = 0
largest = 0
digits = ""
for ch in text:
    if ch == " ":
        # A number has just ended
        number = int(digits)
        count += 1
        total += number
        if number > largest:
            largest = number
        digits = ""
    else:
        digits = digits + ch
# The last number ends with the text, not with a space
number = int(digits)
count += 1
total += number
if number > largest:
    largest = number

# Print the statistics
print(f"Numbers: {count}")
print(f"Total: {total}")
print(f"Largest: {largest}")

# Draw a bar for each number
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
