word = input("Word? ")
vowels = 0
for ch in word:
    if ch == "a" or "e" or "i" or "o" or "u":
        vowels += 1
print(vowels)
