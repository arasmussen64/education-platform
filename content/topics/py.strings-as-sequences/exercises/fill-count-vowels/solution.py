word = input("Word? ")
vowels = 0
for ch in word:
    if ch == "a" or ch == "e" or ch == "i" or ch == "o" or ch == "u":
        vowels += 1
print(vowels)
