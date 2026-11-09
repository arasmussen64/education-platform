text = input("Text? ")
words = 0
letters = 0
word = ""
longest = ""
for ch in text:
    if ch == " ":
        words += 1
        if len(word) > len(longest):
            longest = word
        word = ""
    else:
        letters += 1
        word = word + ch
print(f"Words: {words}")
print(f"Letters: {letters}")
print(f"Longest word: {longest}")
for ch in text:
    if ch == " ":
        print()
    else:
        print("#", end="")
