def shout(text):
    return text.upper() + "!"


def whisper(text):
    return text.lower() + "..."


def apply(func, text):
    return func(text)


print(apply(shout, "hello"))
print(apply(whisper, "HELLO"))
print(sorted(["pear", "fig", "banana"], key=len))
print(sorted([3, -7, 5], key=abs))
print(list(map(len, ["a", "bbb"])))
