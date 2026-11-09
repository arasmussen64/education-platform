text = input("Text? ")
words = 0
letters = len(text)
word = ""
longest = ""
for ch in text:
    if ch == " ":
        words += 1
        if len(word) > len(longest):
            longest = word
        word = ""
    else:
        word = word + ch
words += 1
if len(word) > len(longest):
    longest = word
print(f"Words: {words}")
print(f"Letters: {letters}")
print(f"Longest word: {longest}")
for ch in text:
    if ch == " ":
        print()
    else:
        print("#", end="")
print()
