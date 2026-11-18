# Five made-up trading days for one stock: open, high, low, close, volume.
days = [
    {"day": "Mon", "open": 50.00, "high": 51.20, "low": 49.80, "close": 51.00, "volume": 120000},
    {"day": "Tue", "open": 51.10, "high": 51.50, "low": 50.20, "close": 50.40, "volume": 95000},
    {"day": "Wed", "open": 50.40, "high": 53.90, "low": 50.30, "close": 53.60, "volume": 310000},
    {"day": "Thu", "open": 53.50, "high": 54.00, "low": 52.70, "close": 53.00, "volume": 140000},
    {"day": "Fri", "open": 52.80, "high": 53.40, "low": 52.10, "close": 53.20, "volume": 101000},
]

# One bar: how the day went, and how far apart its extremes were.
for bar in days:
    move = bar["close"] - bar["open"]
    width = bar["high"] - bar["low"]
    print(f"{bar['day']}: {move:+.2f} from open to close, range {width:.2f}")

# The week as one bar: first open, highest high, lowest low, last close.
high = days[0]["high"]
low = days[0]["low"]
volume = 0
busiest = days[0]
for bar in days:
    high = max(high, bar["high"])
    low = min(low, bar["low"])
    volume = volume + bar["volume"]
    if bar["volume"] > busiest["volume"]:
        busiest = bar
print(f"week: open {days[0]['open']:.2f}, high {high:.2f}, low {low:.2f}, close {days[-1]['close']:.2f}")
print(f"volume {volume:,}, busiest day {busiest['day']}")

# Returns are measured from one close to the next.
for i in range(1, len(days)):
    change = days[i]["close"] / days[i - 1]["close"] - 1
    print(f"{days[i]['day']}: {change * 100:+.2f}%")
