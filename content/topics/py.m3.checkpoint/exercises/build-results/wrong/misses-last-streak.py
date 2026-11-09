results = input("Results? ")
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
        if streak > longest:
            longest = streak
        streak = 0
print(f"Games: {games}")
print(f"Wins: {wins}")
print(f"Longest winning streak: {longest}")
streak = 0
for result in results:
    if result == "W":
        print("#", end="")
        streak += 1
    else:
        if streak > 0:
            print()
        streak = 0
