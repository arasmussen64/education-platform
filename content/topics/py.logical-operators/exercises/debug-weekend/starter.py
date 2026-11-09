day = input("Day? ")
temperature = float(input("Temperature? "))
weekend = day == "Sat" or "Sun"
beach_day = weekend and temperature >= 20
stay_in = not weekend or temperature < 5
print("Weekend:", weekend)
print("Beach day:", beach_day)
print("Stay in:", stay_in)
