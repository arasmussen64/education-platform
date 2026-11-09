# Read the week
days = input("Days (s for sun, r for rain)? ")

# Count the days and find the longest sunny streak
sunny = 0
rainy = 0
streak = 0
longest = 0
for day in days:
    if day == "r":
        # A sunny streak has just ended (it may have been empty)
        rainy += 1
        if streak > longest:
            longest = streak
        streak = 0
    else:
        sunny += 1
        streak += 1
# The last streak ends with the week, not with rain
if streak > longest:
    longest = streak

# Print the statistics
print(f"Sunny days: {sunny}")
print(f"Rainy days: {rainy}")
print(f"Longest sunny streak: {longest}")

# Draw a bar for each kind of day
print("Sun:  ", end="")
for _ in range(sunny):
    print("#", end="")
print()
print("Rain: ", end="")
for _ in range(rainy):
    print("#", end="")
print()
