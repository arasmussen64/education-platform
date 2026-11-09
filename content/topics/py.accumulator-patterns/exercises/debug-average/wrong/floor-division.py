how_many = int(input("How many? "))
total = 0
for _ in range(how_many):
    n = int(input("Number? "))
    total += n
average = total // how_many
print(f"Average: {average:.1f}")
