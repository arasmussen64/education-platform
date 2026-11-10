def evens(numbers):
    return [n for n in numbers if n % 2 == 0]


def lengths(words):
    return {w: len(w) for w in words}


def initials(names):
    return sorted({name[0] for name in names})


print(evens([1, 2, 3, 4, 5, 6]))
print(lengths(["sun", "moon"]))
print(initials(["Ada", "Bob", "Alan"]))
