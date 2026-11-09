# Read the text
text = input("Text? ")

# Count the words and letters
words = 0
letters = 0
for ch in text:
    if ch == " ":
        words += 1
    else:
        letters += 1
# The last word ends with the text, not with a space
words += 1

# Print the statistics
print(f"Words: {words}")
print(f"Letters: {letters}")
