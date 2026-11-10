def remaining(hours):
    return 200 - 100 * (hours / 6)


for h in range(0, 25, 6):
    print(f"{h} h: {remaining(h):.1f} mg")
