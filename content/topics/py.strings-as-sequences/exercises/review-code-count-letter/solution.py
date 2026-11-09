word = input("Word? ")
letter = input("Letter? ")
count = 0
for ch in word:
    if ch == letter:
        count += 1
print(count)
