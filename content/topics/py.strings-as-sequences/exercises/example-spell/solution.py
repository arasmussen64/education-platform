word = "python"
print("First:", word[0])
print("Last:", word[-1])
print("Middle:", word[1:4])
position = 0
for ch in word:
    print(position, ch)
    position += 1
print("Length:", len(word))
