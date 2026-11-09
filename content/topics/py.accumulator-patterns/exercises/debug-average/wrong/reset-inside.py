how_many = int(input("How many? "))
for _ in range(how_many):
    total = 0
    n = int(input("Number? "))
    total += n
average = total / how_many
print(f"Average: {average:.1f}")
