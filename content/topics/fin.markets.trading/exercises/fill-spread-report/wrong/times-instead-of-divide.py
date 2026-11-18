quotes = {"ABC": {"bid": 24.98, "ask": 25.02}, "TINY": {"bid": 3.10, "ask": 3.30}, "BIG": {"bid": 149.50, "ask": 150.50}}

for name in quotes:
    quote = quotes[name]
    spread = quote["ask"] - quote["bid"]
    middle = (quote["bid"] + quote["ask"]) / 2
    percent = spread * middle * 100
    print(f"{name}: spread {spread:.2f}, {percent:.2f}% of the middle")
