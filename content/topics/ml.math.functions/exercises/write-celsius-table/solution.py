def to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


for c in range(0, 101, 25):
    print(f"{c} C = {to_fahrenheit(c):.1f} F")
