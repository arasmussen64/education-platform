# Read the results
results = input("Results? ")

# Count the games and wins, and find the longest winning streak
games = 0
wins = 0
streak = 0
longest = 0
for result in results:
    games += 1
    if result == "W":
        wins += 1
        streak += 1
    else:
        # A loss ends the current streak
        if streak > longest:
            longest = streak
        streak = 0
# The last streak ends with the season, not with a loss
if streak > longest:
    longest = streak

# Print the statistics
print(f"Games: {games}")
print(f"Wins: {wins}")
print(f"Longest winning streak: {longest}")

# Draw a bar for each winning streak
streak = 0
for result in results:
    if result == "W":
        print("#", end="")
        streak += 1
    else:
        if streak > 0:
            print()
        streak = 0
if streak > 0:
    print()
