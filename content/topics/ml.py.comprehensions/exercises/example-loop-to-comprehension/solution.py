numbers = [1, 2, 3, 4, 5]
squares = []
for n in numbers:
    squares.append(n * n)
print(squares)

squares = [n * n for n in numbers]
print(squares)

even_squares = [n * n for n in numbers if n % 2 == 0]
print(even_squares)

words = ["apple", "fig", "avocado"]
lengths = {w: len(w) for w in words}
print(lengths)
print(sorted({w[0] for w in words}))
