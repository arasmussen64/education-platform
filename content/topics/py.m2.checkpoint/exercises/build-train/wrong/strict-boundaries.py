distance = float(input("Distance (km)? "))
time = input("Time (peak/offpeak)? ")
railcard = input("Railcard (yes/no)? ")
if distance < 10:
    kind = "short"
    fare = 2.5
elif distance < 50:
    kind = "medium"
    fare = 6
else:
    kind = "long"
    fare = 15
if time == "peak":
    fare = fare + 1.5
if railcard == "yes":
    fare = fare * 2 / 3
print(f"Journey: {kind}")
print(f"Fare: ${fare:.2f}")
