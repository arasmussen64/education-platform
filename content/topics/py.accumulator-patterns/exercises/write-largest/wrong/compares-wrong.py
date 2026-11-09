how_many = int(input("How many? "))
largest = 0
for _ in range(how_many):
    n = int(input("Number? "))
    if n < largest:
        largest = n
print(largest)
