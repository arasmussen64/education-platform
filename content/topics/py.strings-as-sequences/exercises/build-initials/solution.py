name = input("Full name? ")
initials = name[0]
position = 1
while position < len(name):
    if name[position - 1] == " ":
        initials = initials + name[position]
    position += 1
print(initials)
