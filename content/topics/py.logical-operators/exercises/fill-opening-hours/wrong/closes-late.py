hour = int(input("Hour (0-23)? "))
if hour >= 9 and hour <= 17:
    print("Open")
else:
    print("Closed")
print("Lunch break:", hour == 12 or hour == 13)
