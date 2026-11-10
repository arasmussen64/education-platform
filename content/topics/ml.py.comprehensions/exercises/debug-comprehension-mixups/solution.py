numbers = [2, 7, 8, 4, 5]
words = ["tea", "bread"]

# The even numbers, in order.
evens = [n for n in numbers if n % 2 == 0]
print(evens)

# Each word mapped to its length.
lengths = {w: len(w) for w in words}
print(lengths)
