hours = float(input("Hours? "))
day = input("Day? ")
if day == "Sun" or "sun":
    fee = 0
elif hours <= 1:
    fee = 2
elif hours <= 3:
    fee = 5
else:
    fee = 12
print(f"Fee: ${fee:.2f}")
