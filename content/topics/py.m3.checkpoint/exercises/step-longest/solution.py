# Read the text
text = input("Text? ")

# Count the words and letters, and find the longest word
words = 0
letters = 0
word = ""
longest = ""
for ch in text:
    if ch == " ":
        # A word has just ended
        words += 1
        if len(word) > len(longest):
            longest = word
        word = ""
    else:
        letters += 1
        word = word + ch
# The last word ends with the text, not with a space
words += 1
if len(word) > len(longest):
    longest = word

# Print the statistics
print(f"Words: {words}")
print(f"Letters: {letters}")
print(f"Longest word: {longest}")
